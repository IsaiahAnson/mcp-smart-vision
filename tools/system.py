"""System operation tools for MCP server."""

import os
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Dict, Any


def execute_command(command: str, working_dir: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute shell commands with output capture."""
    try:
        if working_dir:
            cwd = Path(working_dir).resolve()
            if not cwd.exists():
                return {"success": False, "error": f"Working directory does not exist: {working_dir}"}
        else:
            cwd = None
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "working_dir": str(cwd) if cwd else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout} seconds"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_disk_usage(path: str = None) -> Dict[str, Any]:
    """Get disk space information."""
    try:
        if path:
            path_obj = Path(path).resolve()
            if not path_obj.exists():
                return {"success": False, "error": f"Path does not exist: {path}"}
            target = str(path_obj)
        else:
            target = "/"
        
        usage = shutil.disk_usage(target)
        
        return {
            "success": True,
            "path": target,
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "total_human": _format_size(usage.total),
            "used_human": _format_size(usage.used),
            "free_human": _format_size(usage.free),
            "percent_used": round((usage.used / usage.total) * 100, 2)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    try:
        return {
            "success": True,
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "user": os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USERNAME', 'unknown')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_environment_variable(name: str) -> Dict[str, Any]:
    """Get environment variable value."""
    try:
        value = os.environ.get(name)
        
        return {
            "success": True,
            "name": name,
            "value": value,
            "exists": value is not None
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def set_environment_variable(name: str, value: str) -> Dict[str, Any]:
    """Set environment variable (for current process only)."""
    try:
        os.environ[name] = value
        
        return {
            "success": True,
            "name": name,
            "value": value,
            "message": "Environment variable set (current process only)"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


# Tool definitions for MCP server
SYSTEM_TOOLS = [
    {
        "name": "execute_command",
        "description": "Execute a shell command",
        "function": execute_command,
        "parameters": {
            "command": {"type": "string", "required": True},
            "working_dir": {"type": "string", "required": False},
            "timeout": {"type": "integer", "required": False, "default": 30}
        }
    },
    {
        "name": "get_disk_usage",
        "description": "Get disk usage information",
        "function": get_disk_usage,
        "parameters": {
            "path": {"type": "string", "required": False}
        }
    },
    {
        "name": "get_system_info",
        "description": "Get system information",
        "function": get_system_info,
        "parameters": {}
    },
    {
        "name": "get_environment_variable",
        "description": "Get environment variable value",
        "function": get_environment_variable,
        "parameters": {
            "name": {"type": "string", "required": True}
        }
    },
    {
        "name": "set_environment_variable",
        "description": "Set environment variable value",
        "function": set_environment_variable,
        "parameters": {
            "name": {"type": "string", "required": True},
            "value": {"type": "string", "required": True}
        }
    }
]
