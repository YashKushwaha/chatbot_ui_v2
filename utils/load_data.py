import os
import subprocess
import json
import chromadb
import requests

from utils.setup_services import CHROMA_DB_PORT

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DOWNLOAD_LOCATION =  os.path.join(PROJECT_ROOT, 'local_only', 'hotpot_qa')
os.makedirs(DOWNLOAD_LOCATION, exist_ok=True)

DATASET_URL = 'http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_fullwiki_v1.json'

def download_hotpot_qa_dataset(dataset_url, data_location):
    
    file_name = dataset_url.split('/')[-1]
    output_path = os.path.join(data_location, file_name)

    if not os.path.exists(output_path):
        print('HotPotQA dataset will be downloaded and saved as -> ', output_path)
        subprocess.run(["curl", "-L", "-o", output_path, dataset_url], check=True)
        print('Done')
    else:
        print('Dataset already exists')

def load_hotpot_qa_dataset():
    file_name = DATASET_URL.split('/')[-1]
    file_to_load = os.path.join(DOWNLOAD_LOCATION, file_name)

    if not os.path.exists(file_to_load):
        download_hotpot_qa_dataset(DATASET_URL, DOWNLOAD_LOCATION)
    
    with open(file_to_load, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_chroma_db_client():
    client = chromadb.HttpClient(
        host="localhost",
        port=int(CHROMA_DB_PORT))
    return client

def upload_pipeline():
    data = load_hotpot_qa_dataset()
    client = get_chroma_db_client()

def condense_context(context):
    return {i[0]: ''.join(i[1]) for i in context}

def process_record(record):
    data = dict(record)
    context = data.pop('context')
    condensed_context = condense_context(context)
    _id = data.pop('_id')
    supporting_facts = data.pop('supporting_facts')
    supporting_facts = '||'.join({i[0] for i in supporting_facts})
    metadata = dict(answer = data.pop('answer'), type = data.pop('type'), level=data.pop('level'), 
                    question = data.pop('question'), supporting_facts=supporting_facts)

    documents = list(condensed_context.values())
    ids = [f'{_id}_{i}' for i in range(len(documents))]
    metadatas = [dict(**metadata, title=title)   for title in condensed_context.keys()]
    
    return dict(documents=documents, metadatas=metadatas, ids=ids)

def get_embeddings(documents):
    url = "http://localhost:8020/batch_embed"

    payload = json.dumps({
    "texts": documents})
    
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

if __name__ == '__main__':
    data = load_hotpot_qa_dataset()
    client = get_chroma_db_client()
    collection = client.get_or_create_collection(name="hot_pot_qa_v2")
    print('Num records -> ', len(data))
    print('Progress : ')
    for index, record in enumerate(data, start=1):
        try:
            batch = process_record(record)
            documents = batch['documents']
            embeddings = get_embeddings(documents)['embeddings']
            batch['embeddings'] = embeddings
            collection.upsert(**batch)
            if index % 10 == 0:
                print(index, end='\t')
        except Exception as e:
            print('\n')
            print(index)
            print(e)
