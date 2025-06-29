import subprocess
import time

import os

CHROMA_DB_PORT = "8010"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

db_location =  os.path.join(PROJECT_ROOT, 'local_only', 'chroma_db')


if __name__ == '__main__':
    # Launch embedding model server
    embed_proc = subprocess.Popen(["python", "utils/embeddings_server.py"])

    # Launch ChromaDB server
    chroma_proc = subprocess.Popen([
        "chroma",
        "run",
        "--path", db_location,
        "--host", "localhost",
        "--port", CHROMA_DB_PORT
    ])

    # Keep main script alive
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Shutting down servers...")
        embed_proc.terminate()
        chroma_proc.terminate()
