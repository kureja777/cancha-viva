"""Protección mínima de la demostración publicada; HTTPS lo aporta el alojamiento."""
import os
import base64
import binascii
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class AccesoAdministrador(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.produccion = os.getenv('APP_ENV', 'local').lower() == 'production'
        self.usuario = os.getenv('WEB_AUTH_USER', '')
        self.clave = os.getenv('WEB_AUTH_PASSWORD', '')
        if self.produccion and (not self.usuario or len(self.clave) < 16):
            raise RuntimeError('Configura WEB_AUTH_USER y WEB_AUTH_PASSWORD de al menos 16 caracteres.')

    async def dispatch(self, request, call_next):
        if not self.produccion or request.url.path == '/health' or request.method == 'OPTIONS':
            return await call_next(request)
        valido = False
        try:
            scheme, token = request.headers.get('authorization', '').split(' ', 1)
            if scheme.lower() == 'basic':
                user, password = base64.b64decode(token, validate=True).decode('utf-8').split(':', 1)
                a = secrets.compare_digest(user.encode(), self.usuario.encode())
                b = secrets.compare_digest(password.encode(), self.clave.encode())
                valido = a and b
        except (ValueError, UnicodeError, binascii.Error):
            pass
        if not valido:
            return JSONResponse({'detail':'Inicia sesión con el acceso de demostración.'},status_code=401,
                                headers={'WWW-Authenticate':'Basic realm="Cancha Viva", charset="UTF-8"','Cache-Control':'no-store'})
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        return response
