from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


import os

import asyncio
from llama_index.llms.ollama import Ollama

from pathlib import Path
from config_settings import *

from back_end.routes import ui_routes, debug_routes, api_routes
from src.agent_list import get_function_agent
from src.response_utils import stream_agent_response
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

model = "qwen3:14b"
context_window = 1000

llm = Ollama(
    model=model,
    request_timeout=120.0,
    thinking=True,
    context_window=context_window,
)

# Create ReAct Agent with tool
agent = get_function_agent(llm=llm)

app.state.agent = agent


if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)