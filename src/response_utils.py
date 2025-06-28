import asyncio
from llama_index.core.agent.workflow import AgentStream

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