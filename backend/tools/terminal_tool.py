from __future__ import annotations

import asyncio
import platform
import subprocess
from pathlib import Path
from typing import Type

from langchain_core.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from config import get_settings


BLOCKED_PATTERNS = (
    "rm -rf /",
    "shutdown",
    "reboot",
    "mkfs",
    "format ",
    ":(){:|:&};:",
)


class TerminalToolInput(BaseModel):
    command: str = Field(..., description="Shell command to execute inside the project root")


class TerminalTool(BaseTool):
    name: str = "terminal"
    description: str = (
        "Execute shell commands inside the project root. Use this for quick inspection, "
        "building, or local commands. Dangerous system-destructive commands are blocked."
    )
    args_schema: Type[BaseModel] = TerminalToolInput
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _root_dir: Path = PrivateAttr()

    def __init__(self, root_dir: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self._root_dir = root_dir

    def _run(
        self,
        command: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        lowered = command.lower()
        if any(pattern in lowered for pattern in BLOCKED_PATTERNS):
            return "Blocked: command matches the terminal blacklist."

        settings = get_settings()
        shell_command = (
            ["powershell", "-NoProfile", "-Command", command]
            if platform.system().lower().startswith("win")
            else ["bash", "-lc", command]
        )
        try:
            completed = subprocess.run(
                shell_command,
                cwd=self._root_dir,
                capture_output=True,
                text=True,
                timeout=settings.terminal_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "Timed out after 30 seconds."

        combined = (completed.stdout or "") + (completed.stderr or "")
        combined = combined.strip() or "[no output]"
        return combined[:5000]

    async def _arun(
        self,
        command: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return await asyncio.to_thread(self._run, command, None)
