from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json
import os
#from back_end.config_settings import templates
import yaml
import datetime

def get_readable_time(timestamp_ms):
    timestamp_s = timestamp_ms / 1000
    readable_time = datetime.datetime.utcfromtimestamp(timestamp_s)
    return readable_time.strftime("%Y-%m-%d %H:%M:%S UTC")

def load_meta_yaml(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")
    
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    
    return data

def is_experiment_folder(folder_name, base_path):
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.isdir(folder_path):
        return False
    if folder_name == "models" or folder_name.startswith("."):
        return False
    meta_file = os.path.join(folder_path, "meta.yaml")
    return os.path.isfile(meta_file)


router = APIRouter()

@router.get("/mlflow/list-experiments", response_class=JSONResponse)
def list_experiments(request: Request):
    mlflow_logs_dir = request.app.state.mlflow_logs_dir
    experiment_folders = [
        folder for folder in os.listdir(mlflow_logs_dir)
        if is_experiment_folder(folder, mlflow_logs_dir)
    ]
    experiment_names = []
    for folder in experiment_folders:
        meta_file = os.path.join(mlflow_logs_dir, folder, 'meta.yaml')
        meta_data = load_meta_yaml(meta_file)
        name = meta_data['name']
        experiment_names.append(name)
    return JSONResponse({'experiments': experiment_names})


@router.get("/mlflow/list-traces", response_class=JSONResponse)
def list_traces(request: Request, db):
    mlflow_logs_dir = request.app.state.mlflow_logs_dir
    experiment_folders = [
        folder for folder in os.listdir(mlflow_logs_dir)
        if is_experiment_folder(folder, mlflow_logs_dir)
    ]
    relevant_folder = None
    for folder in experiment_folders:
        meta_file = os.path.join(mlflow_logs_dir, folder, 'meta.yaml')
        meta_data = load_meta_yaml(meta_file)
        name = meta_data['name']
        if name == db:
            relevant_folder = folder 
    
    if relevant_folder is None:
        return JSONResponse({'collections': []})
    
    traces_folder = os.path.join(mlflow_logs_dir, relevant_folder, 'traces')
    if not os.path.exists(traces_folder):
        traces = []
    else:
        traces = os.listdir(traces_folder)
    
    traces = [extract_trace_creation_time(i, traces_folder) for i in traces]
    return JSONResponse({'collections': traces})


def extract_trace_creation_time(trace_folder, base_dir):
    file_to_read  = os.path.join(base_dir, trace_folder, 'trace_info.yaml')
    if os.path.exists(file_to_read):
        meta_data = load_meta_yaml(file_to_read)
        timestamp = meta_data['timestamp_ms']
        timestamp = get_readable_time(timestamp)
    else:
        timestamp = ''

    return timestamp

