from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
#from back_end.config_settings import templates

router = APIRouter()

@router.get("/mongo_db_stats", response_class=JSONResponse)
def db_stats(request: Request):
    system_dbs = {"admin", "config", "local"}
    client = request.app.state.mongo_db_client
    user_db_list = [i for i in client.list_database_names() if i not in system_dbs]
    return JSONResponse({'databases': user_db_list})

@router.get("/mongo_db_stats/list_collections", response_class=JSONResponse)
def list_collections(request: Request, database_name):
    client = request.app.state.mongo_db_client
    system_dbs = {"admin", "config", "local"}
    if database_name in [i for i in client.list_database_names() if i not in system_dbs]:
        collections = client[database_name].list_collection_names()
    else:
        collections = None
    return JSONResponse({'collections': collections})