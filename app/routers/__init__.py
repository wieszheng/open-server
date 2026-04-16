"""路由模块"""
from app.routers.scripts import router as scripts_router
from app.routers.console import router as console_router
from app.routers.test_cases import router as test_cases_router
from app.routers.directories import router as directories_router
from app.routers.workflows import router as workflows_router
from app.routers.run_jobs import router as run_jobs_router

__all__ = [
    "scripts_router",
    "console_router",
    "test_cases_router",
    "directories_router",
    "workflows_router",
    "run_jobs_router",
]
