import subprocess
import time

import os

CHROMA_DB_PORT = "8010"
EMBEDDING_SERVER_PORT = "8020"

MONGO_DB_PORT = "27017"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

db_location =  os.path.join(PROJECT_ROOT, 'local_only', 'chroma_db')
mongo_data_location = os.path.join(PROJECT_ROOT, 'local_only', 'mongo_db')
    # Launch MongoDB Docker container

def get_mongo_db_commands():
    mongo_cmd = [
        "docker", "run", "-d",
        "--name", "mongodb",
        "-p", f"{MONGO_DB_PORT}:27017",
        "-v", f"{mongo_data_location}:/data/db",
        "mongo"
    ]
    return mongo_cmd

def get_chroma_db_commands():
    commands = [
        "chroma",
        "run",
        "--path", db_location,
        "--host", "localhost",
        "--port", CHROMA_DB_PORT
    ]
    return commands

def get_embedding_server_commands():
    commands = [
    "uvicorn",
    "utils.embeddings_server:app",
    "--host", "127.0.0.1",
    "--port", f"{EMBEDDING_SERVER_PORT}"
    ]
    return commands

def container_exists(container_name):
    """Check if a container exists (running or stopped)"""
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}} {{.Status}}"],
        capture_output=True, text=True
    )
    output = result.stdout.strip()
    return output if output else None

if __name__ == '__main__':

    #embed_proc = subprocess.Popen(["python", "utils/embeddings_server.py"])
    embed_proc = subprocess.Popen(get_embedding_server_commands())    
    chroma_proc = subprocess.Popen(get_chroma_db_commands())

    # Check for existing MongoDB container
    container_info = container_exists("mongodb")

    mongo_proc = subprocess.run(get_mongo_db_commands(), capture_output=True, text=True)
    if container_info:
        container_id, status = container_info.split(' ', 1)
        print(f"MongoDB container found: {container_id} - {status}")

        if "Up" in status:
            print("MongoDB is already running.")
        else:
            print("Starting existing MongoDB container...")
            subprocess.run(["docker", "start", "mongodb"])
    
    
    if mongo_proc.returncode != 0:
        print(f"Failed to start MongoDB: {mongo_proc.stderr}")
    else:
        print(f"MongoDB started with container ID: {mongo_proc.stdout.strip()}")

    # Keep main script alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        embed_proc.terminate()
        chroma_proc.terminate()
        subprocess.run(["docker", "stop", "mongodb"])