
from pathlib import Path
import os
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from datasets import load_dataset
import chromadb
from pymongo import MongoClient

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_squad_documents(max_docs=None, download_location=None):
    download_location = download_location or CACHE_DIR
    dataset = load_dataset("rajpurkar/squad_v2", cache_dir=download_location)
    print('SQUAD data will be downloaded to ', download_location)
    documents = []
    max_docs = max_docs or len(dataset['train'])

    for i in dataset['train'].select(range(max_docs)):       
        #document = process_squad_item(i)
        document = process_squad_record_for_mongo_db(i)
        yield document
        #documents.append(document)
    #return documents

def process_squad_record_for_mongo_db(raw_record):
    record = dict(raw_record)
    _id = record.pop('id')
    answers = record.pop('answers')
    answer_start = '||'.join([str(i) for i in answers.pop('answer_start')])
    answers = "||".join(answers['text'])
    return dict(**record, _id=_id, answers=answers, answer_start=answer_start)

def upload_docs_to_mongo_db_collection(collection, doc_generator, batch_size = None):
    batch_size = batch_size or 100
    batch = []
    print('Docs inserted:')
    counter = 1
    for document in doc_generator:
        batch.append(document)
        
        if len(batch) >= batch_size:
            collection.insert_many(batch)
            batch.clear()

            print(counter*batch_size, end='\t')
            counter+=1
    # Insert remaining documents
    if batch:
        collection.insert_many(batch)



"""
def process_squad_item(item):
    # Extract context
    context = item.pop("context")

    # Flatten answers dictionary
    answers_dict = item.get("answers", {})
    flat_answers = "; ".join(answers_dict.get("text", []))
    first_answer_start = (
        answers_dict.get("answer_start", [None])[0]
        if answers_dict.get("answer_start")
        else None
    )

    # Prepare flat metadata
    metadata = {
        "id": item.get("id"),
        "title": item.get("title"),
        "question": item.get("question"),
        "answers": flat_answers,
        "answer_start": first_answer_start
    }

    return Document(text=context, metadata=metadata)
"""




def create_vector_index(documents, embed_model, vec_store_location):
    os.makedirs(vec_store_location, exist_ok=True)
    db_exists = Path(vec_store_location).exists()

    db = chromadb.PersistentClient(path=vec_store_location)
    chroma_collection = db.get_or_create_collection("my_collection")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if chroma_collection.count() == 0:
        print("No vectors found. Creating new index...")
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model=embed_model)
    else:
        print(f"Loaded existing collection with {chroma_collection.count()} vectors.")
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context, embed_model=embed_model)
   
    return index

def get_index_from_squad_dataset(embed_model):
    documents = load_squad_documents(download_location = CACHE_DIR)
    print('Num documents ->', len(documents))

    vec_store_location = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "vector_store")   
    os.makedirs(vec_store_location, exist_ok=True) 
    
    index = create_vector_index(documents, embed_model, vec_store_location)
    return index

if __name__ == '__main__':
    documents = load_squad_documents()
    client = MongoClient("mongodb://localhost:27017/")
    db = client["agent_evaluation_db"]
    collection = db["squad_dataset"]
    batch_size = 100
    upload_docs_to_mongo_db_collection(collection, documents, batch_size = batch_size)
    print('Done')
    #embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    #index =get_index_from_squad_dataset(embed_model)
    #print('Done')