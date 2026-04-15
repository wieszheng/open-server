"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    scripts_router,
    console_router,
    test_cases_router,
    directories_router,
    workflows_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理。

    启动时初始化数据库，关闭时清理资源。
    """
    # 启动时初始化数据库
    await init_db()
    yield
    # 关闭时清理资源


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="脚本市场 API - 基于 FastAPI 构建的脚本管理和测试用例编排系统",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(scripts_router)
app.include_router(console_router)
app.include_router(test_cases_router)
app.include_router(directories_router)
app.include_router(workflows_router)


@app.get("/")
async def root() -> dict:
    """根路径"""
    return {"message": "Script Market API", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict:
    """健康检查"""
    return {"status": "ok"}
