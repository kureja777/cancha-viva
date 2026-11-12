"""Prueba de concurrencia e integridad sobre una base aislada y desechable."""
import sys,os,json
from uuid import uuid4
from pathlib import Path
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'.runtime'))
sys.path.insert(0,str(root/'backend'))
out=root.parent/'materiales'
out.mkdir(exist_ok=True)
test_db=out/('verificacion_'+uuid4().hex[:8]+'.db')
os.environ['DATABASE_URL']='sqlite:///'+test_db.as_posix()
os.environ['TEST_LOCAL']='1'
from main import app,hoy,engine
from fastapi.testclient import TestClient
client=TestClient(app)
turno={'cancha_id':2,'cliente_id':1,'fecha':str(hoy()+timedelta(days=2)),'hora':14}
with ThreadPoolExecutor(max_workers=8) as pool:
    results=list(pool.map(lambda _:client.post('/api/reservas',json=turno),range(8)))
codes=[r.status_code for r in results]
assert codes.count(201)==1 and codes.count(409)==7,codes
created=next(r.json() for r in results if r.status_code==201)
assert float(created['precio'])==100
assert client.post(f"/api/reservas/{created['id']}/cancelar").status_code==200
assert client.post('/api/reservas',json=turno).status_code==201
assert client.post('/api/reservas',json={**turno,'fecha':str(hoy()-timedelta(days=1))}).status_code==422
assert client.post('/api/reservas',json={**turno,'hora':22}).status_code==422
assert client.post('/api/reservas',json={**turno,'cancha_id':9999}).status_code==404
assert client.post('/api/clientes',json={'codigo':'DEMO-001','nombre':'Duplicado'}).status_code==409
report={'solicitudes_simultaneas':8,'creadas':codes.count(201),'conflictos':codes.count(409),'cancelacion_libera_turno':True,'fecha_pasada_rechazada':True,'hora_invalida_rechazada':True,'cancha_inexistente_rechazada':True,'codigo_cliente_unico':True,'precio_obtenido_del_servidor':True,'base_probada':'SQLite aislada','fecha':str(hoy())}
(out/'verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True))
engine.dispose()
test_db.unlink(missing_ok=True)
