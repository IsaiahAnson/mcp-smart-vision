"""
GUI Automation Tools for MCP Server
Provides tools for interacting with desktop GUI applications.
"""

import pyautogui
import time
import base64
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to corner to abort
pyautogui.PAUSE = 0.5  # Pause between actions


def take_screenshot(region=None):
    """
    Take a screenshot of the screen or a specific region.
    
    Args:
        region: Optional tuple (x, y, width, height) for specific region
    
    Returns:
        dict: Screenshot data including base64 encoded image
    """
    try:
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert to base64 for transmission
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "success": True,
            "width": screenshot.width,
            "height": screenshot.height,
            "image_base64": img_str,
            "message": "Screenshot captured successfully"
        }
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def move_mouse(x, y, duration=0.5):
    """
    Move mouse to specific coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        duration: Time to take for movement (seconds)
    
    Returns:
        dict: Result of operation
    """
    try:
        pyautogui.moveTo(x, y, duration=duration)
        return {
            "success": True,
            "position": {"x": x, "y": y},
            "message": f"Mouse moved to ({x}, {y})"
        }
    except Exception as e:
        logger.error(f"Mouse move failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def click_mouse(x=None, y=None, button='left', clicks=1):
    """
    Click mouse at current position or specific coordinates.
    
    Args:
        x: Optional X coordinate
        y: Optional Y coordinate
        button: 'left', 'right', or 'middle'
        clicks: Number of clicks (1 for single, 2 for double)
    
    Returns:
        dict: Result of operation
    """
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, clicks=clicks, button=button)
            position = {"x": x, "y": y}
        else:
            pyautogui.click(clicks=clicks, button=button)
            position = pyautogui.position()
            position = {"x": position[0], "y": position[1]}
        
        return {
            "success": True,
            "position": position,
            "button": button,
            "clicks": clicks,
            "message": f"{button.capitalize()} clicked {clicks} time(s)"
        }
    except Exception as e:
        logger.error(f"Mouse click failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def type_text(text, interval=0.05):
    """
    Type text using keyboard.
    
    Args:
        text: Text to type
        interval: Delay between keystrokes (seconds)
    
    Returns:
        dict: Result of operation
    """
    try:
        pyautogui.write(text, interval=interval)
        return {
            "success": True,
            "text": text,
            "length": len(text),
            "message": f"Typed {len(text)} characters"
        }
    except Exception as e:
        logger.error(f"Type text failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def press_key(key, presses=1, interval=0.1):
    """
    Press a keyboard key.
    
    Args:
        key: Key name (e.g., 'enter', 'tab', 'ctrl', 'alt', 'shift', 'esc')
        presses: Number of times to press
        interval: Delay between presses (seconds)
    
    Returns:
        dict: Result of operation
    """
    try:
        pyautogui.press(key, presses=presses, interval=interval)
        return {
            "success": True,
            "key": key,
            "presses": presses,
            "message": f"Pressed '{key}' {presses} time(s)"
        }
    except Exception as e:
        logger.error(f"Press key failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def hotkey(keys):
    """
    Press a combination of keys (hotkey).
    
    Args:
        *keys: Keys to press together (e.g., 'ctrl', 'c' for copy)
    
    Returns:
        dict: Result of operation
    """
    try:
        pyautogui.hotkey(*keys)
        return {
            "success": True,
            "keys": list(keys),
            "message": f"Pressed hotkey: {'+'.join(keys)}"
        }
    except Exception as e:
        logger.error(f"Hotkey failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def locate_image_on_screen(image_path, confidence=0.8):
    """
    Find an image on the screen.
    
    Args:
        image_path: Path to image file to find
        confidence: Match confidence (0.0 to 1.0)
    
    Returns:
        dict: Location of image if found
    """
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location:
            center = pyautogui.center(location)
            return {
                "success": True,
                "found": True,
                "location": {
                    "left": location.left,
                    "top": location.top,
                    "width": location.width,
                    "height": location.height
                },
                "center": {"x": center.x, "y": center.y},
                "message": "Image found on screen"
            }
        else:
            return {
                "success": True,
                "found": False,
                "message": "Image not found on screen"
            }
    except Exception as e:
        logger.error(f"Locate image failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_screen_size():
    """
    Get the screen resolution.
    
    Returns:
        dict: Screen width and height
    """
    try:
        size = pyautogui.size()
        return {
            "success": True,
            "width": size.width,
            "height": size.height,
            "message": f"Screen size: {size.width}x{size.height}"
        }
    except Exception as e:
        logger.error(f"Get screen size failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_mouse_position():
    """
    Get current mouse position.
    
    Returns:
        dict: Current X and Y coordinates
    """
    try:
        position = pyautogui.position()
        return {
            "success": True,
            "x": position.x,
            "y": position.y,
            "message": f"Mouse at ({position.x}, {position.y})"
        }
    except Exception as e:
        logger.error(f"Get mouse position failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def scroll(clicks, direction='down'):
    """
    Scroll the mouse wheel.
    
    Args:
        clicks: Number of scroll clicks (positive or negative)
        direction: 'up' or 'down' (for clarity)
    
    Returns:
        dict: Result of operation
    """
    try:
        scroll_amount = clicks if direction == 'down' else -clicks
        pyautogui.scroll(scroll_amount)
        return {
            "success": True,
            "clicks": clicks,
            "direction": direction,
            "message": f"Scrolled {direction} {clicks} clicks"
        }
    except Exception as e:
        logger.error(f"Scroll failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Tool definitions for MCP server
GUI_TOOLS = [
    {
        "name": "take_screenshot",
        "description": "Take a screenshot of the screen or specific region",
        "function": take_screenshot,
        "parameters": {
            "region": {
                "type": "array",
                "required": False,
                "description": "Optional [x, y, width, height] for specific region"
            }
        }
    },
    {
        "name": "move_mouse",
        "description": "Move mouse to specific coordinates",
        "function": move_mouse,
        "parameters": {
            "x": {"type": "integer", "required": True, "description": "X coordinate"},
            "y": {"type": "integer", "required": True, "description": "Y coordinate"},
            "duration": {"type": "number", "required": False, "default": 0.5, "description": "Movement duration in seconds"}
        }
    },
    {
        "name": "click_mouse",
        "description": "Click mouse at current or specific position",
        "function": click_mouse,
        "parameters": {
            "x": {"type": "integer", "required": False, "description": "X coordinate (optional)"},
            "y": {"type": "integer", "required": False, "description": "Y coordinate (optional)"},
            "button": {"type": "string", "required": False, "default": "left", "description": "Mouse button: left, right, or middle"},
            "clicks": {"type": "integer", "required": False, "default": 1, "description": "Number of clicks"}
        }
    },
    {
        "name": "type_text",
        "description": "Type text using keyboard",
        "function": type_text,
        "parameters": {
            "text": {"type": "string", "required": True, "description": "Text to type"},
            "interval": {"type": "number", "required": False, "default": 0.05, "description": "Delay between keystrokes"}
        }
    },
    {
        "name": "press_key",
        "description": "Press a keyboard key",
        "function": press_key,
        "parameters": {
            "key": {"type": "string", "required": True, "description": "Key name (enter, tab, ctrl, etc.)"},
            "presses": {"type": "integer", "required": False, "default": 1, "description": "Number of presses"},
            "interval": {"type": "number", "required": False, "default": 0.1, "description": "Delay between presses"}
        }
    },
    {
        "name": "hotkey",
        "description": "Press a combination of keys",
        "function": hotkey,
        "parameters": {
            "keys": {"type": "array", "required": True, "description": "Array of keys to press together"}
        }
    },
    {
        "name": "get_screen_size",
        "description": "Get screen resolution",
        "function": get_screen_size,
        "parameters": {}
    },
    {
        "name": "get_mouse_position",
        "description": "Get current mouse position",
        "function": get_mouse_position,
        "parameters": {}
    },
    {
        "name": "scroll",
        "description": "Scroll the mouse wheel",
        "function": scroll,
        "parameters": {
            "clicks": {"type": "integer", "required": True, "description": "Number of scroll clicks"},
            "direction": {"type": "string", "required": False, "default": "down", "description": "Direction: up or down"}
        }
    }
]
