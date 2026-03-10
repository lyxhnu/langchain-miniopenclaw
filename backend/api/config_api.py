from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from config import runtime_config

router = APIRouter()


class RagModeRequest(BaseModel):
    enabled: bool


@router.get("/config/rag-mode")
async def get_rag_mode() -> dict[str, bool]:
    return {"enabled": runtime_config.get_rag_mode()}


@router.put("/config/rag-mode")
async def set_rag_mode(payload: RagModeRequest) -> dict[str, bool]:
    config = runtime_config.set_rag_mode(payload.enabled)
    return {"enabled": bool(config["rag_mode"])}
