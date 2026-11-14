import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class BusinessException(Exception):
    """业务异常基类：service 层只管抛，HTTP 表现由处理器统一负责"""
    def __init__(self, code: int, message: str, http_status: int = 400):
        self.code = code
        self.message = message
        self.http_status = http_status

# 常用业务异常（code 段位自定义，这里给个示例规范）
class NotFoundError(BusinessException):
    def __init__(self, resource: str):
        super().__init__(code=40400, message=f"{resource}不存在",
                         http_status=404)

class ConflictError(BusinessException):
    def __init__(self, message: str):
        super().__init__(code=40900, message=message, http_status=409)

def error_body(code: int, message: str, errors=None) -> dict:
    return {"code": code, "message": message, "data": None, "errors": errors}

def register_exception_handlers(app: FastAPI) -> None:
    """在 create_app() 中调用一次，接管四类异常"""

    @app.exception_handler(BusinessException)
    async def business_handler(request: Request, exc: BusinessException):
        return JSONResponse(status_code=exc.http_status,
                            content=error_body(exc.code, exc.message))

    @app.exception_handler(StarletteHTTPException)
    async def http_handler(request: Request, exc: StarletteHTTPException):
        # 把 FastAPI 自己的 404/401/403 也统一成相同格式
        return JSONResponse(status_code=exc.status_code,
                            content=error_body(exc.status_code * 100,
                                               str(exc.detail)),
                            headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        errors = [
            {"field": ".".join(str(x) for x in e["loc"][1:]),
             "message": e["msg"], "type": e["type"]}
            for e in exc.errors()
        ]
        return JSONResponse(status_code=422,
                            content=error_body(42200, "参数校验失败", errors))

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        # 兜底：日志记录详情，对外只给模糊信息（防内部细节泄漏）
        logger.exception("未处理异常: %s %s", request.method, request.url.path)
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(status_code=500,
                            content=error_body(50000, "服务器内部错误"),
                            headers={"X-Request-ID": request_id} if request_id else None)
