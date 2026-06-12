"""
Tools package for MCP Smart Vision Server.

Aggregates every tool category into a single ALL_TOOLS list that the
HTTP server exposes over its REST API.
"""

from .filesystem import FILESYSTEM_TOOLS
from .data import DATA_TOOLS
from .organize import ORGANIZE_TOOLS
from .system import SYSTEM_TOOLS
from .gui_automation import GUI_TOOLS
from .window_automation import WINDOW_TOOLS
from .uia_automation import UIA_TOOLS

# Combine all tools
ALL_TOOLS = (
    FILESYSTEM_TOOLS +
    DATA_TOOLS +
    ORGANIZE_TOOLS +
    SYSTEM_TOOLS +
    GUI_TOOLS +
    WINDOW_TOOLS +
    UIA_TOOLS
)

__all__ = ['ALL_TOOLS']
