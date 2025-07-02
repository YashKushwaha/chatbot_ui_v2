from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
from pymongo.collection import Collection
#from back_end.config_settings import templates

from pymongo.collection import Collection

def mongo_value_counts(collection: Collection, field: str, top_n: int = None) -> list:
    """
    Mimics pandas `value_counts()` for a MongoDB collection.

    Parameters:
        collection (Collection): pymongo collection object
        field (str): Field name to count occurrences for
        top_n (int, optional): Number of top results to return (default: all)

    Returns:
        List of tuples: [(value, count), ...]
    """
    pipeline = [
        {
            "$group": {
                "_id": f"${field}",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        }
    ]
    
    if top_n:
        pipeline.append({"$limit": top_n})
    
    results = collection.aggregate(pipeline)
    
    return [(doc["_id"], doc["count"]) for doc in results]


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

@router.get("/mongo/first-n-records-in-collection", response_class=JSONResponse)
def list_collections(request: Request, db, collection):
    client = request.app.state.mongo_db_client
    records = list(client[db][collection].find().limit(2))
    for doc in records:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
    json_result = json.dumps(records)
    return JSONResponse({"records": records if isinstance(records, list) else []})

@router.get("/mongo/show-value-counts", response_class=JSONResponse)
def list_collections(request: Request, db, collection, key):
    client = request.app.state.mongo_db_client
    collection = client[db][collection]
    counts = mongo_value_counts(collection, key)
    return JSONResponse({"counts": counts if isinstance(counts, list) else []})