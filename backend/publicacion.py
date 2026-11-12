"""Respuestas de la demostración pública sin sesión de usuario."""
from starlette.middleware.base import BaseHTTPMiddleware

class RespuestaDemostracion(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response
