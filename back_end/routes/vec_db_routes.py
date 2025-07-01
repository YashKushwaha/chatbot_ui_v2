from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
#from back_end.config_settings import templates

router = APIRouter()

@router.get("/vecdb/list-collections", response_class=JSONResponse)
def db_stats(request: Request):
    client = request.app.state.vec_db_client
    collection_list = [i.name for i in client.list_collections()]
    return JSONResponse({'collections': collection_list})