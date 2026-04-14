"""路由包"""
from routers.scripts import router as scripts_router
from routers.console import router as console_router
from routers.test_cases import router as test_cases_router
from routers.directories import router as directories_router

__all__ = ["scripts_router", "console_router", "test_cases_router", "directories_router"]
