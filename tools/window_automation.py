"""
Window Automation Tools for MCP Server
Provides tools for managing and interacting with application windows.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import find_windows
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logger.warning("pywinauto not available - window automation features disabled")


def list_windows():
    """
    List all visible windows.
    
    Returns:
        dict: List of windows with titles and handles
    """
    if not PYWINAUTO_AVAILABLE:
        return {"success": False, "error": "pywinauto not installed"}
    
    try:
        desktop = Desktop(backend="uia")
        windows = desktop.windows()
        
        window_list = []
        for window in windows:
            try:
                if window.is_visible():
                    window_list.append({
                        "title": window.window_text(),
                        "class_name": window.class_name(),
                        "handle": window.handle,
                        "is_active": window.has_focus()
                    })
            except:
                continue
        
        return {
            "success": True,
            "windows": window_list,
            "count": len(window_list),
            "message": f"Found {len(window_list)} visible windows"
        }
    except Exception as e:
        logger.error(f"List windows failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def find_window(title_pattern=None, class_name=None):
    """
    Find a window by title pattern or class name.
    
    Args:
        title_pattern: Regex pattern to match window title
        class_name: Window class name to match
    
    Returns:
        dict: Window information if found
    """
    if not PYWINAUTO_AVAILABLE:
        return {"success": False, "error": "pywinauto not installed"}
    
    try:
        kwargs = {}
        if title_pattern:
            kwargs['title_re'] = title_pattern
        if class_name:
            kwargs['class_name'] = class_name
        
        handles = find_windows(**kwargs)
        
        if handles:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=handles[0])
            window = app.window(handle=handles[0])
            
            return {
                "success": True,
                "found": True,
                "title": window.window_text(),
                "class_name": window.class_name(),
                "handle": handles[0],
                "message": f"Found window: {window.window_text()}"
            }
        else:
            return {
                "success": True,
                "found": False,
                "message": "No matching window found"
            }
    except Exception as e:
        logger.error(f"Find window failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def activate_window(title_pattern):
    """
    Bring a window to the foreground.
    
    Args:
        title_pattern: Regex pattern to match window title
    
    Returns:
        dict: Result of operation
    """
    if not PYWINAUTO_AVAILABLE:
        return {"success": False, "error": "pywinauto not installed"}
    
    try:
        handles = find_windows(title_re=title_pattern)
        
        if handles:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=handles[0])
            window = app.window(handle=handles[0])
            window.set_focus()
            
            return {
                "success": True,
                "title": window.window_text(),
                "message": f"Activated window: {window.window_text()}"
            }
        else:
            return {
                "success": False,
                "error": f"No window found matching: {title_pattern}"
            }
    except Exception as e:
        logger.error(f"Activate window failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_window_text(title_pattern):
    """
    Get all text content from a window.
    
    Args:
        title_pattern: Regex pattern to match window title
    
    Returns:
        dict: Window text content
    """
    if not PYWINAUTO_AVAILABLE:
        return {"success": False, "error": "pywinauto not installed"}
    
    try:
        handles = find_windows(title_re=title_pattern)
        
        if handles:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=handles[0])
            window = app.window(handle=handles[0])
            
            # Get all text from window
            texts = []
            try:
                for child in window.descendants():
                    text = child.window_text()
                    if text and text.strip():
                        texts.append(text)
            except:
                pass
            
            return {
                "success": True,
                "title": window.window_text(),
                "texts": texts,
                "count": len(texts),
                "message": f"Retrieved {len(texts)} text elements"
            }
        else:
            return {
                "success": False,
                "error": f"No window found matching: {title_pattern}"
            }
    except Exception as e:
        logger.error(f"Get window text failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def click_button(window_title, button_text):
    """
    Click a button in a window by its text.
    
    Args:
        window_title: Regex pattern to match window title
        button_text: Text on the button to click
    
    Returns:
        dict: Result of operation
    """
    if not PYWINAUTO_AVAILABLE:
        return {"success": False, "error": "pywinauto not installed"}
    
    try:
        handles = find_windows(title_re=window_title)
        
        if handles:
            from pywinauto import Application
            app = Application(backend="uia").connect(handle=handles[0])
            window = app.window(handle=handles[0])
            
            # Find and click button
            button = window.child_window(title=button_text, control_type="Button")
            button.click()
            
            return {
                "success": True,
                "window": window.window_text(),
                "button": button_text,
                "message": f"Clicked button '{button_text}'"
            }
        else:
            return {
                "success": False,
                "error": f"No window found matching: {window_title}"
            }
    except Exception as e:
        logger.error(f"Click button failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Tool definitions for MCP server
WINDOW_TOOLS = [
    {
        "name": "list_windows",
        "description": "List all visible application windows",
        "function": list_windows,
        "parameters": {}
    },
    {
        "name": "find_window",
        "description": "Find a window by title pattern or class name",
        "function": find_window,
        "parameters": {
            "title_pattern": {"type": "string", "required": False, "description": "Regex pattern for window title"},
            "class_name": {"type": "string", "required": False, "description": "Window class name"}
        }
    },
    {
        "name": "activate_window",
        "description": "Bring a window to the foreground",
        "function": activate_window,
        "parameters": {
            "title_pattern": {"type": "string", "required": True, "description": "Regex pattern for window title"}
        }
    },
    {
        "name": "get_window_text",
        "description": "Get all text content from a window",
        "function": get_window_text,
        "parameters": {
            "title_pattern": {"type": "string", "required": True, "description": "Regex pattern for window title"}
        }
    },
    {
        "name": "click_button",
        "description": "Click a button in a window by its text",
        "function": click_button,
        "parameters": {
            "window_title": {"type": "string", "required": True, "description": "Regex pattern for window title"},
            "button_text": {"type": "string", "required": True, "description": "Text on the button"}
        }
    }
]
