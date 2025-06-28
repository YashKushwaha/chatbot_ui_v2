from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi import Form, File, UploadFile
import os

import asyncio
from llama_index.llms.ollama import Ollama
from llama_index.core.agent.workflow import ReActAgent, FunctionAgent, AgentStream
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage

from pathlib import Path
from config_settings import *

from back_end.routes import ui_routes, debug_routes

import mlflow

EMBEDDING_SERVER_PORT = 8001


log_folder = os.path.join(PROJECT_ROOT, 'mlflow_logs')
os.makedirs(log_folder, exist_ok=True)
mlflow.set_tracking_uri(log_folder)
mlflow.set_experiment("agent testing")
mlflow.llama_index.autolog()  # Enable mlflow tracing

app = FastAPI()

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

app.include_router(ui_routes.router)
app.include_router(debug_routes.router) 

def summarize(input: str) -> str:
    return f"Summary: {input[:50]}..."

def get_weather(city_name: str) -> str:
    '''Returns the weather in the input city'''
    return f'Weather is pleasant in {city_name}'

def simple_calculator(math_string : str) -> str:
    '''Can perform simple calculations. Evaluates the input string e.g. 
    simple_calculator("2+3") -> 5
    simple_calculator("2*3") -> 6      
    '''
    try:
        return eval(math_string)
    except Exception as e:
        return f'Error while performing calculation -> {e}'

def run_python_code(code_snippet:str) -> str:
    '''
    Runs the python eval function on input string and returns the output e.g. 
    run_python_code('5*4*3') -> 60
    run_python_code('10 % 3') -> 1    
    '''
    return simple_calculator(code_snippet)

#tool = FunctionTool.from_defaults(fn=summarize, name="Summarization")
weather_tool = FunctionTool.from_defaults(fn=get_weather, name="get_weather")
calc_tool = FunctionTool.from_defaults(fn=simple_calculator, name="simple_calculator")
run_python_code_tool = FunctionTool.from_defaults(fn=run_python_code, name="run_python_code")


model = "qwen3:14b"
context_window = 1000

llm = Ollama(
    model=model,
    request_timeout=120.0,
    thinking=True,
    context_window=context_window,
)

# Create ReAct Agent with tool
#agent = ReActAgent(llm=llm, tools=[tool])

agent = FunctionAgent(llm=llm, tools=[weather_tool, calc_tool, run_python_code_tool])

async def stream_agent_response(agent, prompt: str):
    handler = agent.run(user_msg=prompt)

    async for event in handler.stream_events():
        if isinstance(event, AgentStream):
            delta = event.delta
            if delta:
                yield delta.encode("utf-8")
                await asyncio.sleep(0.2)  # Yield control back to event loop

async def stream_agent_response_old(agent, prompt: str):
    """Yields streamed response text from the ReActAgent."""
    future = agent.run(prompt)

    async for event in future.stream_events():
        if hasattr(event, "response") and event.response:

            if isinstance(event.response, str):
                text = event.response.strip()
                if text:
                    yield text + "\n"

            elif hasattr(event.response, "blocks"):
                blocks = event.response.blocks
                if blocks and blocks[0].text:
                    yield blocks[0].text + "\n"

async def stream_react_agent(agent, prompt: str):
    """Yields streaming text from ReActAgent for FastAPI."""
    future = agent.run(prompt)

    async for event in future.stream_events():
        if hasattr(event, "response") and event.response:

            if isinstance(event.response, str):
                text = event.response.strip()
                if text:
                    yield text + "\n"

            elif hasattr(event.response, "blocks"):
                blocks = event.response.blocks
                if blocks and blocks[0].text:
                    yield blocks[0].text + "\n"

@app.post("/chat_bot")
async def chat_bot(message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_agent_response(agent, message)
    return StreamingResponse(response_stream, media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    app_path = Path(__file__).resolve().with_suffix('').name  # gets filename without .py
    uvicorn.run(f"{app_path}:app", host="localhost", port=8000, reload=True)