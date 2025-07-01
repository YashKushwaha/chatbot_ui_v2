from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
#from back_end.config_settings import templates

router = APIRouter()

@router.get("/mongo/list-databases", response_class=JSONResponse)
def db_stats(request: Request):
    system_dbs = {"admin", "config", "local"}
    client = request.app.state.mongo_db_client
    user_db_list = [i for i in client.list_database_names() if i not in system_dbs]
    return JSONResponse({'databases': user_db_list})

@router.get("/mongo/list-collections", response_class=JSONResponse)
def list_collections(request: Request, db):
    client = request.app.state.mongo_db_client
    system_dbs = {"admin", "config", "local"}
    if db in [i for i in client.list_database_names() if i not in system_dbs]:
        collections = client[db].list_collection_names()
    else:
        collections = None
    return JSONResponse({'collections': collections})

@router.get("/mongo/num-records-in-collection", response_class=JSONResponse)
def list_collections(request: Request, db, collection):
    client = request.app.state.mongo_db_client
    num_records = client[db][collection].count_documents({})
    return JSONResponse({'num_records': num_records})