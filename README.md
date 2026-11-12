# Cancha Viva

Sistema académico de reservas. Datos ficticios. Jhimi Jairo Mamani Blanco.

## Enlaces públicos

Web: https://cancha-viva.vercel.app
API Swagger: https://cancha-viva-api.onrender.com/docs
La demostración abre directamente, sin usuario ni contraseña. Las claves privadas de Supabase permanecen en el servidor.

## Abrir en esta laptop

Haz doble clic en ABRIR_CANCHA_VIVA.cmd. Abre http://127.0.0.1:5173/.
Swagger: http://127.0.0.1:8000/docs. Requiere internet para Supabase.
CERRAR_CANCHA_VIVA.cmd detiene solo los procesos iniciados por el lanzador.

## Ejecutar en otro equipo

Requisitos: Python 3.12 y Node.js 22.12 o posterior compatible con Vite 7.
Instala backend/requirements.txt en un entorno virtual. Copia .env.example a
.env y configura valores privados. Dentro de backend ejecuta
`uvicorn main:app --host 127.0.0.1 --port 8000`.
Dentro de frontend ejecuta `npm install` y `npm run dev -- --host 127.0.0.1`.
No vuelvas a ejecutar los scripts SQL sobre datos existentes sin revisarlos.

## Arquitectura

React y Vite presentan las vistas. Three.js y OrbitControls permiten girar y
acercar una cancha esquemática. Tailwind está configurado junto con CSS propio.
FastAPI aplica reglas y Pydantic valida entradas. El backend usa la Data API
HTTP de Supabase. SQLAlchemy sirve para el modo de pruebas local SQLite.
El índice único parcial impide duplicar un turno confirmado.

## Verificación

backend/verificar.py prueba concurrencia en SQLite temporal, sin modificar
Supabase. backend/verificar_publicacion.py comprueba acceso y CORS.
En frontend, `npm run build` genera dist.

## Seguridad

No compartas .env ni claves. El modo local escucha en loopback. En producción
APP_ENV=production exige la conexión privada a Supabase. HTTPS lo aporta el
alojamiento. Por decisión del titular, la demostración con datos ficticios permite
consultar, registrar y cancelar reservas sin iniciar sesión.
Consulta PUBLICACION.md.
