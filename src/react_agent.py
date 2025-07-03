from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import ReActAgent

from src.embedding_client import RemoteEmbedding

def get_react_agent(Settings):

    vector_store = ChromaVectorStore(
        collection_name="context_vectors",
        host="localhost",
        port=8010
    )

    #storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=Settings.embed_model, llm=Settings.llm)

    query_engine = index.as_query_engine(streaming=False)

    query_engine_tool = QueryEngineTool.from_defaults(
        query_engine,
        name="vector_database_search",
        description=(
            "Use this tool to answer any questions that require external factual knowledge, "
            "detailed technical information, or context that may not be part of your internal knowledge. "
            "also try to check this tool first before checking your internal knowledge"
            "Always prefer this tool when uncertain."
        )
    )
    agent = ReActAgent(tools = [query_engine_tool], llm=Settings.llm)

    return agent