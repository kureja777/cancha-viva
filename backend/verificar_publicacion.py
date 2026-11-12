"""Prueba de publicación sobre SQLite temporal sin usar claves reales."""
from pathlib import Path
import os,sys,tempfile
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.runtime'))
os.environ['APP_ENV']='production';os.environ['TEST_LOCAL']='1'
os.environ.pop('WEB_AUTH_USER',None);os.environ.pop('WEB_AUTH_PASSWORD',None)
os.environ['CORS_ORIGINS']='https://cancha.example'
with tempfile.TemporaryDirectory(dir=root) as tmp:
    os.environ['DATABASE_URL']='sqlite:///'+(Path(tmp)/'prueba.db').as_posix()
    from fastapi.testclient import TestClient
    from main import app,engine,hoy
    from datetime import timedelta
    with TestClient(app) as c:
        assert c.get('/health').status_code==200
        for path in ['/api/salud','/api/canchas','/docs','/openapi.json']:
            assert c.get(path).status_code==200,path
        assert c.get('/api/canchas').status_code==200
        assert c.get('/api/canchas').status_code==200
        r=c.post('/api/reservas',json={'cancha_id':1,'cliente_id':1,'fecha':str(hoy()+timedelta(days=1)),'hora':10})
        assert r.status_code==201,r.text
        pre=c.options('/api/canchas',headers={'Origin':'https://cancha.example','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'authorization'})
        assert pre.status_code==200 and pre.headers['access-control-allow-origin']=='https://cancha.example'
        bad=c.options('/api/canchas',headers={'Origin':'https://otro.example','Access-Control-Request-Method':'GET'})
        assert 'access-control-allow-origin' not in bad.headers
    engine.dispose()
import subprocess
env=os.environ.copy();env['TEST_LOCAL']='';env['SUPABASE_URL']='';env['SUPABASE_SERVICE_ROLE_KEY']=''
env['PYTHONPATH']=os.pathsep.join([str(root/'.runtime'),str(root/'backend')])
r=subprocess.run([sys.executable,'-X','utf8','-c','import main'],env=env,capture_output=True)
assert r.returncode!=0 and b'Configura la conexi' in r.stderr
print('Demostración pública: 200 sin sesión, reserva 201, CORS exacto y conexión privada obligatoria. SQLite aislada.')
