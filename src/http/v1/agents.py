from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.agents_service import AgentsService


class AgentRequest(BaseModel):
    messages: str


router = APIRouter(tags=["agents"])
agents_service = AgentsService()


@router.post("/agents/completions")
async def completions(request: AgentRequest):
    if request.messages is None or request.messages == "":
        raise HTTPException(status_code=400, detail="Messages is required")

    return await agents_service.invoke(request.messages)
