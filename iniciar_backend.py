import sys
from pathlib import Path
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'.runtime'))
sys.path.insert(0,str(root/'backend'))
import uvicorn
uvicorn.run('main:app',host='127.0.0.1',port=8000)
