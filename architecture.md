# Smart Vision Upgrade: UI Automation Architecture

## Overview
The Smart Vision upgrade transitions the MCP server from "Pixel-Based" interaction to "Element-Based" interaction using the Windows UI Automation (UIA) framework.

## Key Components

### 1. UI Inspector (uia_tools.py)
- **inspect_window(title_re)**: Scans a window and returns a hierarchical tree of all UI elements (buttons, text fields, menus).
- **find_element(window_title, element_name, control_type)**: Locates a specific element's coordinates and properties.

### 2. Element Interactor
- **click_element(window_title, element_name)**: Finds and clicks a specific UI element by name.
- **set_element_value(window_title, element_name, value)**: Directly sets text in a field without "typing" it key-by-key.
- **get_element_text(window_title, element_name)**: Reads text from a specific UI component.

### 3. Backend
- Uses `pywinauto` with the `uia` backend for modern Windows 11 application support.
- Fallback to `win32` backend for legacy applications.

## Benefits
- **Speed**: No need to transfer large screenshots for every action.
- **Accuracy**: Clicks are based on element IDs, not estimated coordinates.
- **Robustness**: Works even if windows are resized or moved.
