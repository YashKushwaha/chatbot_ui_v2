
from src.tool_list import get_tool_list
from llama_index.core.agent.workflow import FunctionAgent

TOOL_LIST = get_tool_list()

def get_function_agent(llm):
    agent = FunctionAgent(llm=llm, tools = TOOL_LIST)
    return agent