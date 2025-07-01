from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


import os

import asyncio


from pathlib import Path
from config_settings import *

from back_end.routes import ui_routes, debug_routes, api_routes, db_routes
from src.agent_list import get_function_agent
from src.react_agent import get_react_agent
from src.components import get_ollama_llm, get_mongo_db_client

import mlflow

log_folder = os.path.join(PROJECT_ROOT, 'mlflow_logs')
os.makedirs(log_folder, exist_ok=True)
mlflow.set_tracking_uri(log_folder)
mlflow.set_experiment("agent testing")
mlflow.llama_index.autolog()  # Enable mlflow tracing

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui_routes.router)
app.include_router(debug_routes.router) 
app.include_router(api_routes.router) 
app.include_router(db_routes.router) 



llm = get_ollama_llm()
mongo_db_client = get_mongo_db_client()

# Create ReAct Agent with tool
#agent = get_function_agent(llm=llm)

#agent = get_react_agent(llm=llm)
agent = None
app.state.agent = agent
app.state.mongo_db_client = mongo_db_client

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)