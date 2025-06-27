from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import os

from pathlib import Path
from config_settings import *

from routes import ui


import mlflow

EMBEDDING_SERVER_PORT = 8001

log_folder = os.path.join(PROJECT_ROOT, 'mlflow_logs')
os.makedirs(log_folder, exist_ok=True)
mlflow.set_tracking_uri(log_folder)
mlflow.set_experiment("chatbot_debug_logs")
mlflow.llama_index.autolog()  # Enable mlflow tracing


app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)