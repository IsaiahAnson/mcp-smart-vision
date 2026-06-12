import logging
from pywinauto import Desktop, Application
import time

logger = logging.getLogger(__name__)

def inspect_window(title_re):
    """
    Ultra-safe inspection for Python 3.14.
    Avoids all direct property access that might trigger 'function' errors.
    """
    try:
        desktop = Desktop(backend="uia")
        window = desktop.window(title_re=title_re)
        if not window.exists():
            return {"success": False, "error": f"Window '{title_re}' not found."}
        
        elements = []
        # We only get the top-level descendants to be safe
        for element in window.descendants():
            try:
                # We use a very defensive approach to get ANY identifying info
                info = {}
                
                try:
                    info["name"] = str(element.window_text())
                except:
                    info["name"] = "Unknown"
                
                # We completely avoid .control_type and use .element_info instead
                try:
                    info["control_type"] = str(element.element_info.control_type)
                except:
                    info["control_type"] = "Unknown"
                
                try:
                    info["is_visible"] = bool(element.is_visible())
                except:
                    info["is_visible"] = True

                elements.append(info)
                if len(elements) >= 50: break # Limit for stability
            except:
                continue
                
        return {
            "success": True,
            "window_title": title_re,
            "element_count": len(elements),
            "elements": elements
        }
    except Exception as e:
        return {"success": False, "error": f"UIA Error: {str(e)}"}

def click_ui_element(window_title, element_name, control_type=None):
    try:
        app = Application(backend="uia").connect(title_re=window_title)
        window = app.window(title_re=window_title)
        # Use a more direct search
        element = window.child_window(best_match=element_name)
        element.click_input()
        return {"success": True, "message": f"Clicked {element_name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_ui_element_value(window_title, element_name, value, control_type=None):
    try:
        app = Application(backend="uia").connect(title_re=window_title)
        window = app.window(title_re=window_title)
        element = window.child_window(best_match=element_name)
        element.set_edit_text(value)
        return {"success": True, "message": f"Set {element_name} to {value}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_ui_element_text(window_title, element_name, control_type=None):
    try:
        app = Application(backend="uia").connect(title_re=window_title)
        window = app.window(title_re=window_title)
        element = window.child_window(best_match=element_name)
        return {"success": True, "text": str(element.window_text())}
    except Exception as e:
        return {"success": False, "error": str(e)}

UIA_TOOLS = [
    {
        "name": "inspect_window",
        "description": "Get a list of all UI elements in a window",
        "parameters": {
            "type": "object",
            "properties": {"title_re": {"type": "string"}},
            "required": ["title_re"]
        }
    },
    {
        "name": "click_ui_element",
        "description": "Click a UI element by name",
        "parameters": {
            "type": "object",
            "properties": {
                "window_title": {"type": "string"},
                "element_name": {"type": "string"}
            },
            "required": ["window_title", "element_name"]
        }
    },
    {
        "name": "set_ui_element_value",
        "description": "Set text in a UI element",
        "parameters": {
            "type": "object",
            "properties": {
                "window_title": {"type": "string"},
                "element_name": {"type": "string"},
                "value": {"type": "string"}
            },
            "required": ["window_title", "element_name", "value"]
        }
    },
    {
        "name": "get_ui_element_text",
        "description": "Read text from a UI element",
        "parameters": {
            "type": "object",
            "properties": {
                "window_title": {"type": "string"},
                "element_name": {"type": "string"}
            },
            "required": ["window_title", "element_name"]
        }
    }
]
