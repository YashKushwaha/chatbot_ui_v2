from src.embedding_client import RemoteEmbedding
from pymongo import MongoClient
import chromadb
CHROMA_DB_PORT = 8010

def get_chroma_db_client():
    client = chromadb.HttpClient(
        host="localhost",
        port=int(CHROMA_DB_PORT))
    return client

def fetch_batch(cursor, batch_size):
    """Fetch a batch of records from MongoDB cursor."""
    batch_docs = []
    batch_contexts = []
    
    try:
        for _ in range(batch_size):
            doc = next(cursor)
            batch_docs.append(doc)
            batch_contexts.append(doc['context'])
    except StopIteration:
        pass  # End of cursor

    return batch_docs, batch_contexts

def generate_embeddings(contexts, embed_model):
    """Generate embeddings for a list of contexts."""
    return embed_model._get_text_embedding(contexts)  # Should support batch input


def prepare_metadata(batch_docs):
    """Extract metadata and IDs from documents."""
    metadatas = [{"context_hash": doc['context_hash'], "title": doc['title']} for doc in batch_docs]
    ids = [str(doc['_id']) for doc in batch_docs]
    return metadatas, ids

def insert_to_vec_db(collection, contexts, embeddings, metadatas, ids):
    """Insert records to vector database."""
    collection.add(
        documents=contexts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

def process_batches(cursor, embed_model, vec_db_collection, batch_size=64):
    """Full processing loop: fetch, embed, insert in batches."""
    total_inserted = 0

    while True:
        batch_docs, batch_contexts = fetch_batch(cursor, batch_size)
        
        if not batch_docs:
            break  # No more records

        embeddings = generate_embeddings(batch_contexts, embed_model)
        metadatas, ids = prepare_metadata(batch_docs)
        insert_to_vec_db(vec_db_collection, batch_contexts, embeddings, metadatas, ids)

        total_inserted += len(batch_docs)
        print(f"Inserted {total_inserted} records", end='\r')

    print(f"\nFinished inserting {total_inserted} records.")

if __name__ == '__main__':
    BATCH_SIZE = 128
    EMBEDDING_SERVER_PORT = 8020
    embed_model = RemoteEmbedding(f"http://localhost:{EMBEDDING_SERVER_PORT}")

    vec_db_client = get_chroma_db_client()

    mongo_db_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_db_client["agent_evaluation_db"]
    context_list_collection = db["context_list"]

    cursor = context_list_collection.find({})
    vec_db_collection = vec_db_client.get_or_create_collection(name="context_vectors")

    process_batches(cursor = context_list_collection, 
                    embed_model = embed_model,
                    vec_db_collection=vec_db_collection,
                    batch_size=BATCH_SIZE)