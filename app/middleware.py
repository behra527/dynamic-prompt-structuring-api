
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_body_size: int = 64 * 1024,
    ):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        if request.url.path != "/generate-note":
            return await call_next(request)

        content_length = request.headers.get("content-length")

        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header."},
                )

            if declared_size < 0:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header."},
                )

            if declared_size > self.max_body_size:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body exceeds the 64 KB limit."},
                )

        body = await request.body()

        if len(body) > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body exceeds the 64 KB limit."},
            )

        return await call_next(request)