
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class BodyLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET":
            body = await request.body()
            print(f"{request.url}: Raw Body: {body.decode()}")

            # create a new stream for the body
            async def mock_receive():
                return {"type": "http.request", "body": body}

            # replace the request's receive function with our mock one
            request._receive = mock_receive
        response = await call_next(request)

        return response
