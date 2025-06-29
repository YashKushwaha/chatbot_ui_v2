from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ReActAgent

from src.embedding_client import RemoteEmbedding

def get_react_agent(llm):
    embed_model = RemoteEmbedding(f"http://localhost:8020")

    vector_store = ChromaVectorStore(
        collection_name="hot_pot_qa_v2",
        host="localhost",
        port=8010
    )

    #storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model, llm=llm)

    query_engine = index.as_query_engine(streaming=False)

    query_engine_tool = QueryEngineTool.from_defaults(
        query_engine, name="vector_database_search", description="This tool allows search to vector database"
    )
    agent = ReActAgent(tools = [query_engine_tool], llm=llm)

    return agent