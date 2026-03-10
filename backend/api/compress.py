from __future__ import annotations

from fastapi import APIRouter, HTTPException

from graph.agent import agent_manager

router = APIRouter()


@router.post("/sessions/{session_id}/compress")
async def compress_session(session_id: str) -> dict[str, int]:
    session_manager = agent_manager.session_manager
    if session_manager is None:
        raise HTTPException(status_code=503, detail="Agent manager is not initialized")

    record = session_manager.get_history(session_id)
    messages = record.get("messages", [])
    if len(messages) < 4:
        raise HTTPException(status_code=400, detail="At least 4 messages are required")

    n_messages = max(4, len(messages) // 2)
    summary = await agent_manager.summarize_history(messages[:n_messages])
    result = session_manager.compress_history(session_id, summary, n_messages)
    return result
