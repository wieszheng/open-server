"""
RunJob 内存存储 + SSE 事件总线

create_job_and_run 创建 job 并立即后台执行。
遇到 appUiAction 等委派节点时，暂停并等待浏览器调用 /node-result 回传结果后继续。
执行完成后将结果持久化到数据库。
"""
import asyncio
import time
import uuid
from datetime import datetime, timezone

_jobs: dict[str, dict] = {}
_TTL = 3600


def get_job(job_id: str) -> dict | None:
    job = _jobs.get(job_id)
    if job and time.time() - job["created_at"] > _TTL:
        del _jobs[job_id]
        return None
    return job


async def _push(job: dict, event: dict):
    job["events"].append(event)
    await job["queue"].put(event)
    etype = event.get("type", "")
    if etype == "complete":
        job["status"] = "done"
    elif etype == "node_start" and job["status"] == "pending":
        job["status"] = "running"
    elif etype == "error":
        job["status"] = "error"


async def _persist(job: dict, result: dict, node_results: list[dict], started_at: float):
    """将执行结果写入数据库，更新用例和工作流统计。"""
    from app.database import async_session_maker
    from app.models.test_execution import TestExecution
    from app.models.test_case import TestCase
    from app.models.workflow import Workflow
    from sqlalchemy import select

    duration = time.perf_counter() - started_at
    test_case_id: int = job["test_case_id"]
    passed = result["passed"]
    failed = result["failed"]
    total = result["total"]
    now = datetime.now(timezone.utc)

    async with async_session_maker() as session:
        # 1. 写 TestExecution 记录
        execution = TestExecution(
            timestamp=now,
            duration=duration,
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            test_case_id=test_case_id,
            node_results=node_results,
        )
        session.add(execution)

        # 2. 更新 TestCase 统计
        tc = await session.get(TestCase, test_case_id)
        if tc is not None:
            tc.total_runs += 1
            if failed == 0:
                tc.passed_runs += 1
            else:
                tc.failed_runs += 1
            tc.last_run_time = now
            # 滚动平均耗时
            prev_avg = tc.avg_duration or 0.0
            tc.avg_duration = round(
                (prev_avg * (tc.total_runs - 1) + duration) / tc.total_runs, 3
            )

        # 3. 更新 Workflow 统计
        wf_result = await session.execute(
            select(Workflow).where(Workflow.test_case_id == test_case_id)
        )
        wf = wf_result.scalar_one_or_none()
        if wf is not None:
            wf.total_runs += 1
            wf.last_run_time = now
            wf.last_run_status = "success" if failed == 0 else "failed"

        await session.commit()


async def _run_flow_bg(job: dict, flow: dict):
    from app.executor import execute_flow

    started_at = time.perf_counter()
    node_results: list[dict] = []

    try:
        async def on_start(node_id: str, label: str):
            await _push(job, {"type": "node_start", "node_id": node_id, "label": label})

        async def on_done(node_id: str, label: str, success: bool, message: str, duration: float):
            node_results.append({
                "node_id": node_id,
                "label": label,
                "success": success,
                "message": message,
                "duration": round(duration, 4),
            })
            await _push(job, {
                "type": "node_done",
                "node_id": node_id,
                "label": label,
                "success": success,
                "message": message,
                "duration": duration,
            })

        async def on_delegate(node_id: str, label: str, node_data: dict):
            ev = asyncio.Event()
            result: dict = {}
            job["pending_delegation"] = {"node_id": node_id, "event": ev, "result": result}

            await _push(job, {
                "type": "delegate_to_agent",
                "node_id": node_id,
                "label": label,
                "node_data": node_data,
            })

            try:
                await asyncio.wait_for(ev.wait(), timeout=120.0)
                return result.get("success", False), result.get("message", ""), result.get("duration", 0.0)
            except asyncio.TimeoutError:
                return False, "等待本地 Agent 超时（120s）", 120.0
            finally:
                job.pop("pending_delegation", None)

        result = await execute_flow(
            flow,
            on_node_start=on_start,
            on_node_done=on_done,
            on_node_delegate=on_delegate,
        )

        # 持久化
        await _persist(job, result, node_results, started_at)

        await _push(job, {
            "type": "complete",
            "node_id": None,
            "success": result["failed"] == 0,
            "message": f"{result['passed']}/{result['total']} 通过",
            "duration": None,
        })
    except Exception as exc:
        await _push(job, {"type": "error", "node_id": None, "message": str(exc)})


def create_job_and_run(test_case_id: int, flow: dict) -> str:
    job_id = str(uuid.uuid4())
    job = {
        "id": job_id,
        "test_case_id": test_case_id,
        "status": "pending",
        "created_at": time.time(),
        "queue": asyncio.Queue(),
        "events": [],
        "pending_delegation": None,
    }
    _jobs[job_id] = job
    asyncio.create_task(_run_flow_bg(job, flow))
    return job_id


def resolve_delegation(job_id: str, node_id: str, success: bool, message: str, duration: float) -> bool:
    """浏览器回传本地 Agent 执行结果，恢复暂停的执行引擎。"""
    job = get_job(job_id)
    if job is None:
        return False
    delegation = job.get("pending_delegation")
    if delegation is None or delegation["node_id"] != node_id:
        return False
    delegation["result"].update({"success": success, "message": message, "duration": duration})
    delegation["event"].set()
    return True


async def stream_events(job_id: str):
    job = get_job(job_id)
    if job is None:
        yield {"type": "error", "message": "job not found"}
        return

    for ev in list(job["events"]):
        yield ev
        if ev.get("type") in ("complete", "error"):
            return

    q: asyncio.Queue = job["queue"]
    while True:
        try:
            event = await asyncio.wait_for(q.get(), timeout=60.0)
        except asyncio.TimeoutError:
            yield {"type": "heartbeat"}
            continue
        yield event
        if event.get("type") in ("complete", "error"):
            break

