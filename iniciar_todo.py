"""Inicio local sin rutas de runtime fijas. Solo administra procesos propios."""
from pathlib import Path
import sys, os, subprocess, time, json, urllib.request, webbrowser
ROOT=Path(__file__).resolve().parent
STATE=ROOT/'.procesos_locales.json'
def runtimes():
    current=Path(sys.executable).resolve().parent.parent
    if (current/'node/bin/node.exe').exists():return Path(sys.executable),current/'node/bin/node.exe'
    roots=list(Path('C:/Program Files/WindowsApps').glob('OpenAI.CodexPrimaryRuntime.*/dependencies'))
    for r in sorted(roots,key=lambda p:p.stat().st_mtime,reverse=True):
        py=r/'python/python.exe';node=r/'node/bin/node.exe'
        if py.exists() and node.exists():return py,node
    raise RuntimeError('No se encontraron los runtimes de Codex. Revisa README.md para instalar Python y Node.')
def ready(url):
    try:
        with urllib.request.urlopen(url,timeout=3) as r:return r.status==200
    except Exception:return False
def main():
    if '--stop' in sys.argv:
        rows=json.loads(STATE.read_text()) if STATE.exists() else []
        for row in rows:
            # Evita detener un PID reciclado: consulta el ejecutable y el comando.
            try:
                import ctypes
                k=ctypes.windll.kernel32;k.OpenProcess.restype=ctypes.c_void_p
                handle=k.OpenProcess(0x1000|0x0001,False,row['pid'])
                if not handle:continue
                buf=ctypes.create_unicode_buffer(32768);size=ctypes.c_ulong(len(buf))
                if k.QueryFullProcessImageNameW(ctypes.c_void_p(handle),0,buf,ctypes.byref(size)) and buf.value.lower()==row['exe'].lower():
                    # El tiempo de creación evita confundir otra instancia del mismo ejecutable.
                    created=ctypes.c_ulonglong();exit_t=ctypes.c_ulonglong();kernel=ctypes.c_ulonglong();user=ctypes.c_ulonglong()
                    if k.GetProcessTimes(ctypes.c_void_p(handle),ctypes.byref(created),ctypes.byref(exit_t),ctypes.byref(kernel),ctypes.byref(user)) and created.value==row['created']:
                        k.TerminateProcess(ctypes.c_void_p(handle),0)
                k.CloseHandle(ctypes.c_void_p(handle))
            except OSError:pass
        STATE.unlink(missing_ok=True);print('Servicios del lanzador detenidos.');return
    py,node=runtimes();processes=json.loads(STATE.read_text()) if STATE.exists() else []
    for url,args,cwd,log in [
        ('http://127.0.0.1:8000/api/salud',[str(py),str(ROOT/'iniciar_backend.py')],ROOT,'backend'),
        ('http://127.0.0.1:5173/',[str(node),'node_modules/vite/bin/vite.js','--host','127.0.0.1','--strictPort'],ROOT/'frontend','frontend')]:
        if not ready(url):
            with (ROOT/(log+'.log')).open('a') as out,(ROOT/(log+'_error.log')).open('a') as err:
                proc=subprocess.Popen(args,cwd=cwd,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            import ctypes
            k=ctypes.windll.kernel32;k.OpenProcess.restype=ctypes.c_void_p
            handle=k.OpenProcess(0x1000,False,proc.pid)
            created=ctypes.c_ulonglong();a=ctypes.c_ulonglong();b=ctypes.c_ulonglong();c=ctypes.c_ulonglong()
            k.GetProcessTimes(ctypes.c_void_p(handle),ctypes.byref(created),ctypes.byref(a),ctypes.byref(b),ctypes.byref(c))
            k.CloseHandle(ctypes.c_void_p(handle))
            processes.append({'pid':proc.pid,'exe':args[0],'created':created.value})
            STATE.write_text(json.dumps(processes))
            for _ in range(30):
                if ready(url):break
                if proc.poll() is not None:raise RuntimeError('No pudo iniciar '+log+'. Revisa '+log+'_error.log.')
                time.sleep(.5)
            if not ready(url):raise RuntimeError('El servicio tarda en responder. Revisa '+log+'_error.log.')
    print('Cancha Viva: http://127.0.0.1:5173/\nSwagger: http://127.0.0.1:8000/docs')
    if '--no-browser' not in sys.argv:webbrowser.open('http://127.0.0.1:5173/')
if __name__=='__main__':
    try:main()
    except Exception as e:print('No se pudo completar el inicio:',str(e));sys.exit(1)
