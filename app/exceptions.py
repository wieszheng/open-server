"""应用异常处理"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    请求验证异常处理器。

    Args:
        request: HTTP 请求对象。
        exc: 验证异常对象。

    Returns:
        JSON 响应。
    """
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器。

    Args:
        request: HTTP 请求对象。
        exc: 异常对象。

    Returns:
        JSON 响应。
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册异常处理器到 FastAPI 应用。

    Args:
        app: FastAPI 应用实例。
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
