"""
运行 Job 路由

POST  /run-jobs                       拉取工作流，立即在服务端后台执行
GET   /run-jobs/{job_id}/stream       SSE 实时订阅执行事件
POST  /run-jobs/{job_id}/node-result  浏览器回传本地 Agent 执行结果
GET   /run-jobs/{job_id}              查询状态
"""
import json

from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.run_jobs import create_job_and_run, get_job, resolve_delegation, stream_events
from app.dependencies import get_workflow_service
from app.services import WorkflowService

router = APIRouter(prefix="/run-jobs", tags=["运行任务"])


class CreateJobRequest(BaseModel):
    test_case_id: int


class NodeResultRequest(BaseModel):
    node_id: str
    success: bool
    message: str = ""
    duration: float = 0.0   # seconds


@router.post("")
async def create_run_job(
    body: CreateJobRequest,
    workflow_service: WorkflowService = Depends(get_workflow_service),
) -> dict:
    """拉取工作流后立即在服务端后台执行，返回 job_id 供前端 SSE 订阅。"""
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


@router.post("/{job_id}/node-result")
async def report_node_result(
    body: NodeResultRequest,
    job_id: str = Path(...),
) -> dict:
    """
    浏览器将本地 Agent 的执行结果回传给服务端，恢复暂停的执行引擎。
    """
    ok = resolve_delegation(job_id, body.node_id, body.success, body.message, body.duration)
    if not ok:
        raise HTTPException(status_code=404, detail="job 不存在或无等待中的委派节点")
    return {"ok": True}


@router.get("/{job_id}")
async def get_run_job(job_id: str = Path(...)) -> dict:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job["id"], "status": job["status"], "test_case_id": job["test_case_id"]}


@router.get("/{job_id}/stream")
async def sse_stream(job_id: str = Path(...)):
    """浏览器 SSE 订阅，实时接收执行事件。"""
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
