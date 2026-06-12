"""File organization tools for MCP server."""

import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict


def organize_by_type(source_dir: str, create_folders: bool = True, 
                     dry_run: bool = False) -> Dict[str, Any]:
    """Organize files into folders by extension."""
    try:
        source_obj = Path(source_dir).resolve()
        if not source_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {source_dir}"}
        
        if not source_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {source_dir}"}
        
        organized = defaultdict(list)
        operations = []
        
        for item in source_obj.iterdir():
            if item.is_file():
                ext = item.suffix.lower() or "no_extension"
                ext_clean = ext.lstrip('.')
                
                target_folder = source_obj / ext_clean
                target_path = target_folder / item.name
                
                organized[ext_clean].append(item.name)
                operations.append({
                    "source": str(item),
                    "destination": str(target_path),
                    "extension": ext_clean
                })
                
                if not dry_run:
                    if create_folders:
                        target_folder.mkdir(exist_ok=True)
                    shutil.move(str(item), str(target_path))
        
        return {
            "success": True,
            "source_directory": str(source_obj),
            "dry_run": dry_run,
            "files_organized": sum(len(files) for files in organized.values()),
            "categories": dict(organized),
            "operations": operations
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def organize_by_date(source_dir: str, date_format: str = "%Y-%m", 
                     date_type: str = "modified", dry_run: bool = False) -> Dict[str, Any]:
    """Organize files by creation/modification date."""
    try:
        source_obj = Path(source_dir).resolve()
        if not source_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {source_dir}"}
        
        if not source_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {source_dir}"}
        
        organized = defaultdict(list)
        operations = []
        
        for item in source_obj.iterdir():
            if item.is_file():
                stat = item.stat()
                
                if date_type == "modified":
                    timestamp = stat.st_mtime
                elif date_type == "created":
                    timestamp = stat.st_ctime
                else:
                    return {"success": False, "error": f"Invalid date_type: {date_type}"}
                
                date_str = datetime.fromtimestamp(timestamp).strftime(date_format)
                target_folder = source_obj / date_str
                target_path = target_folder / item.name
                
                organized[date_str].append(item.name)
                operations.append({
                    "source": str(item),
                    "destination": str(target_path),
                    "date_folder": date_str
                })
                
                if not dry_run:
                    target_folder.mkdir(exist_ok=True)
                    shutil.move(str(item), str(target_path))
        
        return {
            "success": True,
            "source_directory": str(source_obj),
            "dry_run": dry_run,
            "date_format": date_format,
            "date_type": date_type,
            "files_organized": sum(len(files) for files in organized.values()),
            "date_folders": dict(organized),
            "operations": operations
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_duplicates(directory: str, recursive: bool = True, 
                    min_size: int = 0) -> Dict[str, Any]:
    """Find duplicate files by content hash."""
    try:
        dir_obj = Path(directory).resolve()
        if not dir_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {directory}"}
        
        if not dir_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory}"}
        
        hashes = defaultdict(list)
        
        # Get all files
        if recursive:
            files = dir_obj.rglob('*')
        else:
            files = dir_obj.glob('*')
        
        # Calculate hashes
        for file in files:
            if file.is_file() and file.stat().st_size >= min_size:
                file_hash = _calculate_hash(file)
                hashes[file_hash].append({
                    "path": str(file),
                    "name": file.name,
                    "size": file.stat().st_size
                })
        
        # Filter to only duplicates
        duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
        
        total_duplicate_files = sum(len(files) - 1 for files in duplicates.values())
        total_wasted_space = sum(
            files[0]["size"] * (len(files) - 1) 
            for files in duplicates.values()
        )
        
        return {
            "success": True,
            "directory": str(dir_obj),
            "duplicate_groups": len(duplicates),
            "total_duplicate_files": total_duplicate_files,
            "wasted_space": total_wasted_space,
            "wasted_space_human": _format_size(total_wasted_space),
            "duplicates": duplicates
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def bulk_rename(directory: str, pattern: str, replacement: str, 
                file_pattern: str = "*", dry_run: bool = False) -> Dict[str, Any]:
    """Rename multiple files with patterns."""
    try:
        dir_obj = Path(directory).resolve()
        if not dir_obj.exists():
            return {"success": False, "error": f"Directory does not exist: {directory}"}
        
        if not dir_obj.is_dir():
            return {"success": False, "error": f"Path is not a directory: {directory}"}
        
        operations = []
        
        for file in dir_obj.glob(file_pattern):
            if file.is_file():
                new_name = file.name.replace(pattern, replacement)
                
                if new_name != file.name:
                    new_path = file.parent / new_name
                    
                    operations.append({
                        "old_name": file.name,
                        "new_name": new_name,
                        "old_path": str(file),
                        "new_path": str(new_path)
                    })
                    
                    if not dry_run:
                        file.rename(new_path)
        
        return {
            "success": True,
            "directory": str(dir_obj),
            "pattern": pattern,
            "replacement": replacement,
            "dry_run": dry_run,
            "files_renamed": len(operations),
            "operations": operations
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _calculate_hash(file_path: Path, algorithm: str = 'md5') -> str:
    """Calculate file hash."""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def _format_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


# Tool definitions for MCP server
ORGANIZE_TOOLS = [
    {
        "name": "organize_by_type",
        "description": "Organize files by type into folders",
        "function": organize_by_type,
        "parameters": {
            "source_dir": {"type": "string", "required": True},
            "create_folders": {"type": "boolean", "required": False, "default": True},
            "file_types": {"type": "object", "required": False}
        }
    },
    {
        "name": "organize_by_date",
        "description": "Organize files by date into folders",
        "function": organize_by_date,
        "parameters": {
            "source_dir": {"type": "string", "required": True},
            "date_format": {"type": "string", "required": False, "default": "%Y-%m"},
            "use_modified_date": {"type": "boolean", "required": False, "default": True}
        }
    },
    {
        "name": "find_duplicates",
        "description": "Find duplicate files by content hash",
        "function": find_duplicates,
        "parameters": {
            "directory": {"type": "string", "required": True},
            "recursive": {"type": "boolean", "required": False, "default": True},
            "min_size": {"type": "integer", "required": False, "default": 0}
        }
    },
    {
        "name": "bulk_rename",
        "description": "Bulk rename files using pattern matching",
        "function": bulk_rename,
        "parameters": {
            "directory": {"type": "string", "required": True},
            "pattern": {"type": "string", "required": True},
            "replacement": {"type": "string", "required": True},
            "preview": {"type": "boolean", "required": False, "default": False}
        }
    }
]
