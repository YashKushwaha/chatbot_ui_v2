import subprocess
import time
import json
import os

CHROMA_DB_PORT = "8010"
EMBEDDING_SERVER_PORT = "8020"
MONGO_DB_PORT = "27017"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

db_location =  os.path.join(PROJECT_ROOT, 'local_only', 'chroma_db')
#mongo_data_location = os.path.join(PROJECT_ROOT, 'local_only', 'mongo_database')
#os.makedirs(mongo_data_location, exist_ok=True)

#print(mongo_data_location)

def get_container_settings(container_name):
    """Retrieve container settings as JSON"""
    result = subprocess.run(
        ["docker", "inspect", container_name],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)[0]
    except (IndexError, json.JSONDecodeError):
        return None

def get_mongo_db_commands():
    mongo_cmd = [
        "docker", "run", "-d",
        "--name", "mongodb-container",
        "-p", f"{MONGO_DB_PORT}:27017",
        "-v", f"{mongo_data_location}:/data/db",
        "mongodb/mongodb-community-server:latest"
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

def container_matches_settings(settings):
    """Check if existing container matches expected port and volume"""
    # Check Port Bindings
    ports = settings.get("NetworkSettings", {}).get("Ports", {})
    EXPECTED_PORT = f"{MONGO_DB_PORT}/tcp"
    port_binding = ports.get(EXPECTED_PORT)
    port_ok = port_binding and port_binding[0].get("HostPort") == MONGO_DB_PORT

    # Check Volume Mounts
    mounts = settings.get("Mounts", [])
    volume_ok = any(
        mount["Destination"] == "/data/db" and os.path.abspath(mount["Source"]) == os.path.abspath(mongo_data_location)
        for mount in mounts
    )

    return port_ok and volume_ok

def remove_container(container_name):
    """Force remove container"""
    subprocess.run(["docker", "rm", "-f", container_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def start_mongo():
    """Run MongoDB container with expected config"""
    subprocess.run([
        "docker", "run", "-d",
        "--name", "mongodb",
        "-p", f"{MONGO_DB_PORT}:27017",
        "-v", f"{mongo_data_location}:/data/db",
        "mongodb/mongodb-community-server:latest"
    ])

"""
Note: I tried to start the mongo db server from within the WSL but it didn't work
So better to start the container from Docker Desktop itself
"""

if __name__ == '__main__':

    #embed_proc = subprocess.Popen(["python", "utils/embeddings_server.py"])
    embed_proc = subprocess.Popen(get_embedding_server_commands())    
    chroma_proc = subprocess.Popen(get_chroma_db_commands())
    # Check for existing MongoDB container
    """
    container_info = container_exists("mongodb")    
    mongo_proc = subprocess.run(get_mongo_db_commands(), capture_output=True, text=True)

    settings = get_container_settings("mongodb")

    if settings:
        if container_matches_settings(settings):
            print("Reusing existing MongoDB container.")
            subprocess.run(["docker", "start", "mongodb"])
        else:
            print("MongoDB container settings differ. Recreating container...")
            remove_container("mongodb")
            start_mongo()
    else:
        print("Creating new MongoDB container...")
        start_mongo()
    """

    # Keep main script alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        embed_proc.terminate()
        chroma_proc.terminate()
        subprocess.run(["docker", "stop", "mongodb"])