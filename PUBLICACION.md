# Publicación de Cancha Viva

Estado al 12 de noviembre de 2026: código publicado, frontend y API comprobados.

GitHub: https://github.com/kureja777/cancha-viva
Frontend: https://cancha-viva.vercel.app
Swagger: https://cancha-viva-api.onrender.com/docs

Las instrucciones siguientes permiten reproducir el despliegue en otra cuenta.

## GitHub

Crea cancha-viva en tu cuenta. Sube solo código y ejemplos. Excluir .env,
.runtime, node_modules, dist, bases, logs y .procesos_locales.json.

## Render

Conecta GitHub, servicio web Python, raíz backend.
Build: `pip install -r requirements.txt`.
Inicio: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
Salud pública /health solo confirma el proceso, no la base.
Variables privadas: APP_ENV=production, SUPABASE_URL,
SUPABASE_SERVICE_ROLE_KEY. Esta demostración pública no requiere WEB_AUTH_USER ni WEB_AUTH_PASSWORD.
CORS_ORIGINS es el origen HTTPS exacto de Vercel sin barra final.
render.yaml describe los valores, sin secretos ni contratación de un plan.

El titular autorizó expresamente el uso de su clave en las variables privadas del
servicio cancha-viva-api de Render. No se incluye esa credencial en el repositorio.
Nunca pongas la clave privada en Vercel ni en variables VITE_.

## Vercel

Importa el repositorio con raíz frontend, framework Vite,
build npm run build y salida dist. VITE_API_BASE_URL es la dirección HTTPS
real de Render, sin /api al final. Añade el origen final de Vercel a Render.

## Comprobación y entrega

Abre directamente la interfaz y Swagger sin iniciar sesión.
Verifica GET 200, POST 201, persistencia y cancelación de una
reserva futura ficticia. Comprueba también el visor 3D.
No basta /health: /api/salud debe comprobar también la base.
Añade al Word solo enlaces comprobados. Sube el PPTX a Canva o a un servicio
compartible y verifica el enlace sin sesión. Graba el video sin credenciales.
LinkedIn requiere revisar y autorizar el texto y video concretos antes de publicar.
