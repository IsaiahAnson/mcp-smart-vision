"""File system operation tools for MCP server."""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import hashlib


def list_directory(path: str, show_hidden: bool = False) -> Dict[str, Any]:
    """List contents of a directory with detailed metadata."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}
        
        if not path_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {path}"}
        
        items = []
        for item in path_obj.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            stat = item.stat()
            items.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": stat.st_size if item.is_file() else None,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            })
        
        return {
            "success": True,
            "path": str(path_obj),
            "items": items,
            "count": len(items)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_file(path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """Read text file contents."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"File does not exist: {path}"}
        
        if not path_obj.is_file():
            return {"success": False, "error": f"Path is not a file: {path}"}
        
        content = path_obj.read_text(encoding=encoding)
        stat = path_obj.stat()
        
        return {
            "success": True,
            "path": str(path_obj),
            "content": content,
            "size": stat.st_size,
            "lines": len(content.splitlines()),
            "encoding": encoding
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> Dict[str, Any]:
    """Write/create text files."""
    try:
        path_obj = Path(path).resolve()
        
        if create_dirs:
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        path_obj.write_text(content, encoding=encoding)
        stat = path_obj.stat()
        
        return {
            "success": True,
            "path": str(path_obj),
            "size": stat.st_size,
            "lines": len(content.splitlines())
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete files or directories."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}
        
        if path_obj.is_dir():
            if recursive:
                shutil.rmtree(path_obj)
            else:
                path_obj.rmdir()  # Only works if empty
        else:
            path_obj.unlink()
        
        return {
            "success": True,
            "path": str(path_obj),
            "message": "Deleted successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move/rename files or directories."""
    try:
        source_obj = Path(source).resolve()
        dest_obj = Path(destination).resolve()
        
        if not source_obj.exists():
            return {"success": False, "error": f"Source does not exist: {source}"}
        
        shutil.move(str(source_obj), str(dest_obj))
        
        return {
            "success": True,
            "source": str(source_obj),
            "destination": str(dest_obj),
            "message": "Moved successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
    """Copy files or directories."""
    try:
        source_obj = Path(source).resolve()
        dest_obj = Path(destination).resolve()
        
        if not source_obj.exists():
            return {"success": False, "error": f"Source does not exist: {source}"}
        
        if dest_obj.exists() and not overwrite:
            return {"success": False, "error": f"Destination already exists: {destination}"}
        
        if source_obj.is_dir():
            shutil.copytree(str(source_obj), str(dest_obj), dirs_exist_ok=overwrite)
        else:
            shutil.copy2(str(source_obj), str(dest_obj))
        
        return {
            "success": True,
            "source": str(source_obj),
            "destination": str(dest_obj),
            "message": "Copied successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_directory(path: str, parents: bool = True) -> Dict[str, Any]:
    """Create new directories."""
    try:
        path_obj = Path(path).resolve()
        path_obj.mkdir(parents=parents, exist_ok=False)
        
        return {
            "success": True,
            "path": str(path_obj),
            "message": "Directory created successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_file_info(path: str) -> Dict[str, Any]:
    """Get detailed file metadata."""
    try:
        path_obj = Path(path).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}
        
        stat = path_obj.stat()
        
        info = {
            "success": True,
            "path": str(path_obj),
            "name": path_obj.name,
            "type": "directory" if path_obj.is_dir() else "file",
            "size": stat.st_size,
            "size_human": _format_size(stat.st_size),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
        }
        
        if path_obj.is_file():
            info["extension"] = path_obj.suffix
        
        return info
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_files(directory: str, pattern: str = "*", recursive: bool = True, 
                 content_search: str = None) -> Dict[str, Any]:
    """Search for files by name pattern or content."""
    try:
        path_obj = Path(directory).resolve()
        if not path_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {directory}"}
        
        if not path_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory}"}
        
        matches = []
        
        if recursive:
            files = path_obj.rglob(pattern)
        else:
            files = path_obj.glob(pattern)
        
        for file in files:
            if file.is_file():
                match_info = {
                    "path": str(file),
                    "name": file.name,
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                }
                
                # Content search if specified
                if content_search:
                    try:
                        content = file.read_text(encoding='utf-8', errors='ignore')
                        if content_search.lower() in content.lower():
                            matches.append(match_info)
                    except:
                        pass  # Skip files that can't be read
                else:
                    matches.append(match_info)
        
        return {
            "success": True,
            "directory": str(path_obj),
            "pattern": pattern,
            "matches": matches,
            "count": len(matches)
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
FILESYSTEM_TOOLS = [
    {
        "name": "list_directory",
        "description": "List contents of a directory",
        "function": list_directory,
        "parameters": {
            "path": {"type": "string", "required": True},
            "show_hidden": {"type": "boolean", "required": False, "default": False}
        }
    },
    {
        "name": "read_file",
        "description": "Read text file contents",
        "function": read_file,
        "parameters": {
            "path": {"type": "string", "required": True},
            "encoding": {"type": "string", "required": False, "default": "utf-8"}
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "function": write_file,
        "parameters": {
            "path": {"type": "string", "required": True},
            "content": {"type": "string", "required": True},
            "encoding": {"type": "string", "required": False, "default": "utf-8"}
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file or directory",
        "function": delete_file,
        "parameters": {
            "path": {"type": "string", "required": True},
            "recursive": {"type": "boolean", "required": False, "default": False}
        }
    },
    {
        "name": "move_file",
        "description": "Move or rename a file/directory",
        "function": move_file,
        "parameters": {
            "source": {"type": "string", "required": True},
            "destination": {"type": "string", "required": True}
        }
    },
    {
        "name": "copy_file",
        "description": "Copy a file or directory",
        "function": copy_file,
        "parameters": {
            "source": {"type": "string", "required": True},
            "destination": {"type": "string", "required": True},
            "overwrite": {"type": "boolean", "required": False, "default": False}
        }
    },
    {
        "name": "create_directory",
        "description": "Create a new directory",
        "function": create_directory,
        "parameters": {
            "path": {"type": "string", "required": True},
            "parents": {"type": "boolean", "required": False, "default": True}
        }
    },
    {
        "name": "get_file_info",
        "description": "Get detailed information about a file",
        "function": get_file_info,
        "parameters": {
            "path": {"type": "string", "required": True}
        }
    },
    {
        "name": "search_files",
        "description": "Search for files by pattern",
        "function": search_files,
        "parameters": {
            "directory": {"type": "string", "required": True},
            "pattern": {"type": "string", "required": True},
            "recursive": {"type": "boolean", "required": False, "default": True},
            "content_search": {"type": "string", "required": False}
        }
    }
]
