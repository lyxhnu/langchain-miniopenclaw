from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Type

from langchain_core.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr


class ReadFileInput(BaseModel):
    path: str = Field(..., description="Relative path inside the project root")


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read a local file under the project root. Use relative paths like skills/foo/SKILL.md."
    args_schema: Type[BaseModel] = ReadFileInput
    model_config = ConfigDict(arbitrary_types_allowed=True)
    _root_dir: Path = PrivateAttr()

    def __init__(self, root_dir: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self._root_dir = root_dir.resolve()

    def _resolve_path(self, path: str) -> Path:
        candidate = (self._root_dir / path).resolve()
        if self._root_dir not in candidate.parents and candidate != self._root_dir:
            raise ValueError("Path traversal detected.")
        return candidate

    def _run(
        self,
        path: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        try:
            file_path = self._resolve_path(path)
        except ValueError as exc:
            return f"Read failed: {exc}"
        if not file_path.exists():
            return "Read failed: file does not exist."
        if file_path.is_dir():
            return "Read failed: path is a directory."
        return file_path.read_text(encoding="utf-8")[:10000]

    async def _arun(
        self,
        path: str,
        run_manager: AsyncCallbackManagerForToolRun | None = None,
    ) -> str:
        return await asyncio.to_thread(self._run, path, None)
