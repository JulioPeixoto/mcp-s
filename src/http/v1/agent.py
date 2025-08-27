from fastapi import APIRouter, HTTPException

from src.services.agents_service import AgentsService


router = APIRouter(tags=["agents"])
agents_service = AgentsService()

@router.post("/agents/completions")
async def completions(messages: str):
    if messages is None or messages == "":
        raise HTTPException(status_code=400, detail="Messages is required")

    return await agents_service.invoke(messages)
