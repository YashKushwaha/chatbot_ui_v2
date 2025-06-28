from src.response_utils import stream_agent_response
from fastapi import Form, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/chat_bot")
async def chat_bot(request: Request, message: str = Form(...), image: UploadFile = File(None)):
    response_stream = stream_agent_response(request.app.state.agent, message)
    return StreamingResponse(response_stream, media_type="text/plain")