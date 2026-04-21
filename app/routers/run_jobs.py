"""
运行 Job 路由

POST  /run-jobs                       拉取工作流，立即在服务端后台执行
GET   /run-jobs/{job_id}/stream       SSE 实时订阅执行事件
POST  /run-jobs/{job_id}/node-result  浏览器回传本地 Agent 执行结果
GET   /run-jobs/{job_id}              查询状态

GET   /test-cases/{case_id}/execution  该用例最新执行结果（含节点截图 base64）
"""
import json

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.run_jobs import create_job_and_run, get_job, resolve_delegation, stream_events
from app.dependencies import get_workflow_service
from app.services import WorkflowService

router = APIRouter(tags=["运行任务"])

_run_router = APIRouter(prefix="/run-jobs")
_exec_router = APIRouter()


class CreateJobRequest(BaseModel):
    test_case_id: int


class NodeResultRequest(BaseModel):
    node_id: str
    success: bool
    message: str = ""
    duration: float = 0.0
    screenshot: str | None = None


@_run_router.post("")
async def create_run_job(
    body: CreateJobRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    flow = await workflow_service.get_workflow_by_test_case(body.test_case_id)
    if flow is None:
        raise HTTPException(status_code=404, detail="该测试用例尚未编排工作流")
    nodes = flow.nodes if isinstance(flow.nodes, list) else []
    if not nodes:
        raise HTTPException(status_code=400, detail="工作流为空，没有可执行的节点")
    flow_dict = {
        "nodes": nodes,
        "edges": flow.edges if isinstance(flow.edges, list) else [],
    }
    job_id = create_job_and_run(body.test_case_id, flow_dict)
    return {"job_id": job_id, "status": "running"}


@_run_router.post("/{job_id}/node-result")
async def report_node_result(body: NodeResultRequest, job_id: str = Path(...)) -> dict:
    ok = resolve_delegation(
        job_id, body.node_id, body.success, body.message, body.duration,
        screenshot=body.screenshot,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="job 不存在或无等待中的委派节点")
    return {"ok": True}


@_run_router.get("/{job_id}")
async def get_run_job(job_id: str = Path(...)) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job["id"], "status": job["status"], "test_case_id": job["test_case_id"]}


@_run_router.get("/{job_id}/stream")
async def sse_stream(job_id: str = Path(...)):
    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail="job not found")

    async def _generator():
        async for event in stream_events(job_id):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        _generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@_exec_router.get("/test-cases/{case_id}/execution")
async def get_case_execution(case_id: int = Path(...)) -> dict:
    """返回该测试用例最新一次执行结果（含节点截图 base64）。无记录时返回 404。"""
    from app.database import async_session_maker
    from app.models.test_execution import TestExecution
    from sqlalchemy import select

    async with async_session_maker() as session:
        row = await session.execute(
            select(TestExecution).where(TestExecution.test_case_id == case_id)
        )
        e = row.scalars().first()

    if e is None:
        raise HTTPException(status_code=404, detail="该用例尚无执行记录")

    return {
        "timestamp": e.timestamp.isoformat(),
        "duration": round(e.duration, 3),
        "total": e.total_cases,
        "passed": e.passed_cases,
        "failed": e.failed_cases,
        "node_results": e.node_results or [],
    }


router.include_router(_run_router)
router.include_router(_exec_router)
