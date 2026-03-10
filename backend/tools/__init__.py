from __future__ import annotations

from pathlib import Path

from langchain_core.tools import BaseTool

from tools.fetch_url_tool import FetchURLTool
from tools.python_repl_tool import PythonReplTool
from tools.read_file_tool import ReadFileTool
from tools.search_knowledge_tool import SearchKnowledgeBaseTool
from tools.terminal_tool import TerminalTool


def get_all_tools(base_dir: Path) -> list[BaseTool]:
    return [
        TerminalTool(root_dir=base_dir),
        PythonReplTool(root_dir=base_dir),
        FetchURLTool(),
        ReadFileTool(root_dir=base_dir),
        SearchKnowledgeBaseTool(root_dir=base_dir),
    ]
