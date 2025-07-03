from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from llama_index.core import Settings

import os
import asyncio

from pathlib import Path

from back_end.config_settings import *
from constants import EXPERIMENT_NAME, MLFLOW_LOGS_FOLDER

from back_end.routes import ui_routes, debug_routes, api_routes, db_routes, vec_db_routes, mlflow_routes
from src.agent_list import get_function_agent
from src.react_agent import get_react_agent
from src.components import get_ollama_llm, get_mongo_db_client, get_chroma_db_client
from src.embedding_client import RemoteEmbedding
from src.mlflow_utils import MLflowLogs

import mlflow

mlflow.set_tracking_uri(MLFLOW_LOGS_FOLDER)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.llama_index.autolog()  # Enable mlflow tracing

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui_routes.router)
app.include_router(debug_routes.router) 
app.include_router(api_routes.router) 
app.include_router(db_routes.router) 
app.include_router(vec_db_routes.router) 
app.include_router(mlflow_routes.router) 

llm = get_ollama_llm()
embed_model = RemoteEmbedding(f"http://localhost:8020")

Settings.llm = llm
Settings.embed_model = embed_model

mongo_db_client = get_mongo_db_client()
vec_db_client = get_chroma_db_client()
# Create ReAct Agent with tool
#agent = get_function_agent(llm=llm)

agent = get_react_agent(Settings)
#agent = None

mlflow_handler = MLflowLogs(MLFLOW_LOGS_FOLDER)
app.state.agent = agent
app.state.mongo_db_client = mongo_db_client
app.state.vec_db_client = vec_db_client
#app.state.mlflow_logs_dir = MLFLOW_LOGS_FOLDER
app.state.experiment_name = EXPERIMENT_NAME
app.state.mlflow_handler = mlflow_handler

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)