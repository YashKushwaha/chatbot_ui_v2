from pathlib import Path
import os
from pymongo import MongoClient
from datasets import load_dataset
import hashlib


CACHE_DIR = os.path.join(Path(__file__).resolve().parents[1] , "local_only", "data")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_context_hash(context: str) -> str:
    return hashlib.md5(context.encode('utf-8')).hexdigest()

def process_squad_record_for_mongo_db(raw_record):
    record = dict(raw_record)
    _id = record.pop('id')
    answers = record.pop('answers')
    answer_start = '||'.join([str(i) for i in answers.pop('answer_start')])
    answers = "||".join(answers['text'])
    return dict(**record, _id=_id, answers=answers, answer_start=answer_start)


def load_squad_documents(max_docs=None, download_location=None):
    download_location = download_location or CACHE_DIR
    dataset = load_dataset("rajpurkar/squad_v2", cache_dir=download_location)
    print('SQUAD data will be downloaded to ', download_location)
    documents = []
    max_docs = max_docs or len(dataset['train'])

    for i in dataset['train'].select(range(max_docs)):       
        document = process_squad_record_for_mongo_db(i)
        yield document

if __name__ == '__main__':
    documents = load_squad_documents()
    client = MongoClient("mongodb://localhost:27017/")
    db = client["agent_evaluation_db"]
    
    context_list_collection = db["context_list"]
    context_list_collection.create_index("context_hash", unique=True)
    
    qna_collection = db["qna_pairs"]
    qna_collection.create_index("id", unique=True)
    counter = 1

    print('Starting database upload')
    for record in documents:
        context = record['context']
        context_hash = get_context_hash(context)

        context_list_collection.update_one(
        {"context_hash": context_hash},
        {"$setOnInsert": {"context": context, "title": record['title']}},
        upsert=True
        )


        #-----------------------------------
        id = record['_id']
        to_add = dict(title = record['title'], context_hash=context_hash,
                      question=record['question'], answers=record['answers'])
        
        qna_collection.update_one(
        {"id": id},
        {"$setOnInsert": to_add},
        upsert=True
        )

        #------------------------
        counter+=1
        if counter % 1000 == 0:
            print(counter, end='\t')

    print()

    

