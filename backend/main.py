"""API de Cancha Viva. Ejecutar en loopback para la demostración académica."""
import os
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from publicacion import RespuestaDemostracion

ROOT = Path(__file__).resolve().parent
env_file=ROOT.parent/'.env'
if env_file.exists():
    for line in env_file.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            k,v=line.split('=',1);os.environ.setdefault(k.strip(),v.strip())
SUPABASE_URL=os.getenv('SUPABASE_URL','').rstrip('/')
SUPABASE_KEY=os.getenv('SUPABASE_SERVICE_ROLE_KEY','')
CLOUD=bool(SUPABASE_URL and SUPABASE_KEY) and not os.getenv('TEST_LOCAL')
if os.getenv('APP_ENV','local').lower()=='production' and not CLOUD and not os.getenv('TEST_LOCAL'):
    raise RuntimeError('Configura la conexión privada de Supabase antes de publicar.')
def remoto(method,table,params=None,body=None):
    import httpx
    headers={'apikey':SUPABASE_KEY,'Prefer':'return=representation'}
    if SUPABASE_KEY.startswith('eyJ'):
        headers['Authorization']='Bearer '+SUPABASE_KEY
    try:
        r=httpx.request(method,SUPABASE_URL+'/rest/v1/'+table,params=params,
          json=body,headers=headers,timeout=25)
    except httpx.HTTPError:
        raise HTTPException(503,'No se pudo conectar con Supabase. Intenta nuevamente.')
    if r.status_code>=400:
        try: code=r.json().get('code','')
        except ValueError: code=''
        if code=='23505': raise HTTPException(409,'El turno o el código ya está registrado.')
        raise HTTPException(502,'Supabase no pudo completar la operación.')
    return r.json() if r.content else []

DB_URL = os.getenv('DATABASE_URL', 'sqlite:///' + (ROOT / 'cancha_viva.db').as_posix())
if DB_URL.startswith('postgresql://'):
    DB_URL = DB_URL.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {}, pool_pre_ping=True)
app = FastAPI(title='Cancha Viva API', description='Canchas, clientes y reservas por turnos de una hora.', version='1.0.0')
app.add_middleware(RespuestaDemostracion)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip().rstrip('/') for x in os.getenv('CORS_ORIGINS','http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:4173').split(',') if x.strip()], allow_methods=['GET','POST'], allow_headers=['Content-Type','Authorization'])

@app.get('/health',include_in_schema=False)
def health_publico():
    return {'estado':'ok'}

def hoy():
    return datetime.now(ZoneInfo('America/La_Paz')).date()

def filas(sql, params=None):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params or {}).mappings()]

def init_local():
    if CLOUD or not DB_URL.startswith('sqlite'): return
    with engine.begin() as c:
        c.execute(text('PRAGMA foreign_keys=ON'))
        c.execute(text('CREATE TABLE IF NOT EXISTS canchas(id INTEGER PRIMARY KEY,nombre TEXT UNIQUE NOT NULL,deporte TEXT NOT NULL,superficie TEXT NOT NULL,precio_hora NUMERIC NOT NULL CHECK(precio_hora>0),activa BOOLEAN NOT NULL DEFAULT 1)'))
        c.execute(text('CREATE TABLE IF NOT EXISTS clientes(id INTEGER PRIMARY KEY,codigo TEXT UNIQUE NOT NULL,nombre TEXT NOT NULL CHECK(length(trim(nombre))>=3))'))
        c.execute(text("CREATE TABLE IF NOT EXISTS reservas(id INTEGER PRIMARY KEY,cancha_id INTEGER NOT NULL REFERENCES canchas(id),cliente_id INTEGER NOT NULL REFERENCES clientes(id),fecha DATE NOT NULL,hora INTEGER NOT NULL CHECK(hora BETWEEN 7 AND 21),estado TEXT NOT NULL DEFAULT 'confirmada' CHECK(estado IN ('confirmada','cancelada')),precio NUMERIC NOT NULL CHECK(precio>0),created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"))
        c.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS reservas_turno_unico ON reservas(cancha_id,fecha,hora) WHERE estado='confirmada'"))
        if not c.execute(text('SELECT count(*) FROM canchas')).scalar():
            for n,d,s,p in [('Arena Norte','Fútbol 7','Césped sintético',120),('Arena Sur','Fútbol 7','Césped sintético',100),('Polideportivo','Básquet','Piso deportivo',80),('La Terraza','Vóley','Piso deportivo',60)]:
                c.execute(text('INSERT INTO canchas(nombre,deporte,superficie,precio_hora) VALUES (:n,:d,:s,:p)'),dict(n=n,d=d,s=s,p=p))
            for i,n in enumerate(['Aurora','Horizonte','Andino','Valle'],1):
                c.execute(text('INSERT INTO clientes(codigo,nombre) VALUES (:codigo,:nombre)'),dict(codigo=f'DEMO-{i:03d}',nombre=f'Cliente {n}'))
            for ca,cl,h in [(1,1,17),(3,2,19)]:
                c.execute(text('INSERT INTO reservas(cancha_id,cliente_id,fecha,hora,precio) SELECT :ca,:cl,:f,:h,precio_hora FROM canchas WHERE id=:ca'),dict(ca=ca,cl=cl,f=str(hoy()),h=h))
init_local()

class ClienteIn(BaseModel):
    codigo: str = Field(min_length=3,max_length=30,pattern=r'^[A-Za-z0-9-]+$')
    nombre: str = Field(min_length=3,max_length=100)
class ReservaIn(BaseModel):
    cancha_id: int = Field(gt=0)
    cliente_id: int = Field(gt=0)
    fecha: date
    hora: int = Field(ge=7,le=21)

@app.get('/api/salud',tags=['Estado'])
def salud():
    if CLOUD:
        remoto('GET','canchas',{'select':'id','limit':'1'})
        return {'estado':'ok','base':'Supabase PostgreSQL','fecha':str(hoy())}
    filas('SELECT 1')
    return {'estado':'ok','base':'PostgreSQL' if engine.dialect.name=='postgresql' else 'SQLite local','fecha':str(hoy())}

@app.get('/api/canchas',tags=['Canchas'])
def canchas():
    if CLOUD: return remoto('GET','canchas',{'order':'id'})
    return filas('SELECT * FROM canchas ORDER BY id')

@app.get('/api/clientes',tags=['Clientes'])
def clientes():
    if CLOUD: return remoto('GET','clientes',{'order':'id'})
    return filas('SELECT * FROM clientes ORDER BY id')

@app.post('/api/clientes',status_code=201,tags=['Clientes'])
def crear_cliente(data:ClienteIn):
    values={'codigo':data.codigo.strip().upper(),'nombre':data.nombre.strip()}
    if len(values['nombre'])<3: raise HTTPException(422,'El nombre debe contener al menos tres caracteres.')
    if CLOUD: return remoto('POST','clientes',body=values)[0]
    try:
        with engine.begin() as c:
            row=c.execute(text('INSERT INTO clientes(codigo,nombre) VALUES (:codigo,:nombre) RETURNING *'),values).mappings().one()
            return dict(row)
    except IntegrityError: raise HTTPException(409,'El código de cliente ya existe.')

@app.get('/api/reservas',tags=['Reservas'])
def reservas():
    if CLOUD:
        rows=remoto('GET','reservas',{'select':'*,canchas(nombre,deporte),clientes(nombre)','order':'fecha.desc,hora.desc,id.desc'})
        return [{**{k:v for k,v in r.items() if k not in ('canchas','clientes')},'cancha':r['canchas']['nombre'],'deporte':r['canchas']['deporte'],'cliente':r['clientes']['nombre']} for r in rows]
    return filas('SELECT r.*,c.nombre AS cancha,c.deporte,cl.nombre AS cliente FROM reservas r JOIN canchas c ON c.id=r.cancha_id JOIN clientes cl ON cl.id=r.cliente_id ORDER BY r.fecha DESC,r.hora DESC,r.id DESC')

@app.get('/api/disponibilidad',tags=['Reservas'])
def disponibilidad(fecha:date,cancha_id:int=Query(gt=0)):
    if CLOUD:
        if not remoto('GET','canchas',{'id':f'eq.{cancha_id}','select':'id'}): raise HTTPException(404,'Cancha no encontrada.')
        occupied={r['hora'] for r in remoto('GET','reservas',{'cancha_id':f'eq.{cancha_id}','fecha':f'eq.{fecha}','estado':'eq.confirmada','select':'hora'})}
        return [{'hora':h,'disponible':h not in occupied} for h in range(7,22)]
    if not filas('SELECT id FROM canchas WHERE id=:id',{'id':cancha_id}): raise HTTPException(404,'Cancha no encontrada.')
    ocupadas={r['hora'] for r in filas("SELECT hora FROM reservas WHERE cancha_id=:id AND fecha=:f AND estado='confirmada'",{'id':cancha_id,'f':fecha})}
    return [{'hora':h,'disponible':h not in ocupadas} for h in range(7,22)]

@app.post('/api/reservas',status_code=201,tags=['Reservas'])
def crear_reserva(data:ReservaIn):
    now=datetime.now(ZoneInfo('America/La_Paz'))
    if data.fecha<now.date() or (data.fecha==now.date() and data.hora<=now.hour):
        raise HTTPException(422,'Selecciona un turno futuro.')
    if data.fecha>now.date()+timedelta(days=90): raise HTTPException(422,'Se permiten reservas hasta 90 días por adelantado.')
    if CLOUD:
        court=remoto('GET','canchas',{'id':f'eq.{data.cancha_id}'})
        if not court or not court[0]['activa']: raise HTTPException(404,'Cancha no disponible.')
        if not remoto('GET','clientes',{'id':f'eq.{data.cliente_id}','select':'id'}): raise HTTPException(404,'Cliente no encontrado.')
        return remoto('POST','reservas',body={**data.model_dump(mode='json'),'precio':float(court[0]['precio_hora'])})[0]
    try:
        with engine.begin() as c:
            cancha=c.execute(text('SELECT * FROM canchas WHERE id=:id'),{'id':data.cancha_id}).mappings().first()
            if not cancha or not cancha['activa']: raise HTTPException(404,'Cancha no disponible.')
            if not c.execute(text('SELECT id FROM clientes WHERE id=:id'),{'id':data.cliente_id}).first(): raise HTTPException(404,'Cliente no encontrado.')
            params=data.model_dump();params['precio']=cancha['precio_hora']
            row=c.execute(text('INSERT INTO reservas(cancha_id,cliente_id,fecha,hora,precio) VALUES (:cancha_id,:cliente_id,:fecha,:hora,:precio) RETURNING *'),params).mappings().one()
            return dict(row)
    except IntegrityError: raise HTTPException(409,'Ese turno acaba de ocuparse. Elige otro horario.')

@app.post('/api/reservas/{reserva_id}/cancelar',tags=['Reservas'])
def cancelar(reserva_id:int):
    if CLOUD:
        rows=remoto('PATCH','reservas',{'id':f'eq.{reserva_id}'},{'estado':'cancelada'})
        if not rows: raise HTTPException(404,'Reserva no encontrada.')
        return rows[0]
    with engine.begin() as c:
        row=c.execute(text("UPDATE reservas SET estado='cancelada' WHERE id=:id RETURNING *"),{'id':reserva_id}).mappings().first()
        if not row: raise HTTPException(404,'Reserva no encontrada.')
        return dict(row)

@app.get('/api/resumen',tags=['Estado'])
def resumen():
    if CLOUD:
        cs=canchas();cls=clientes();rs=reservas()
        active=[r for r in rs if r['fecha']==str(hoy()) and r['estado']=='confirmada']
        return {'canchas':sum(bool(c['activa']) for c in cs),'clientes':len(cls),'reservas_hoy':len(active),'importe_hoy':sum(float(r['precio']) for r in active)}
    return {'canchas':filas('SELECT count(*) AS n FROM canchas WHERE activa=true')[0]['n'],
      'clientes':filas('SELECT count(*) AS n FROM clientes')[0]['n'],
      'reservas_hoy':filas("SELECT count(*) AS n FROM reservas WHERE fecha=:f AND estado='confirmada'",{'f':hoy()})[0]['n'],
      'importe_hoy':filas("SELECT coalesce(sum(precio),0) AS n FROM reservas WHERE fecha=:f AND estado='confirmada'",{'f':hoy()})[0]['n']}
