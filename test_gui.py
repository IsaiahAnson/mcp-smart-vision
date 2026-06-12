"""
Test script for GUI automation features
Tests the new GUI automation tools with Obsidian
"""

import requests
import json
import time

API_URL = "https://odilia-pharmacodynamical-maryland.ngrok-free.dev/api/v1/tools"
API_KEY = "replace-with-your-generated-key"
headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}


def test_tool(tool_name, parameters=None):
    """Test a specific tool"""
    if parameters is None:
        parameters = {}
    
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"Parameters: {parameters}")
    print(f"{'='*60}")
    
    try:
        r = requests.post(
            f"{API_URL}/{tool_name}",
            headers=headers,
            json={"parameters": parameters},
            timeout=30
        )
        result = r.json()
        
        if result.get("success"):
            print("✓ SUCCESS")
            print(json.dumps(result.get("result", {}), indent=2))
        else:
            print("✗ FAILED")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result
    
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
        return None


def main():
    """Run GUI automation tests"""
    print("\n" + "="*60)
    print("GUI AUTOMATION TEST SUITE")
    print("="*60)
    
    # Test 1: Get screen size
    test_tool("get_screen_size")
    
    # Test 2: Get mouse position
    test_tool("get_mouse_position")
    
    # Test 3: List windows
    result = test_tool("list_windows")
    
    # Test 4: Find Obsidian window
    test_tool("find_window", {"title_pattern": ".*Obsidian.*"})
    
    # Test 5: Take screenshot
    print("\nTaking screenshot (base64 data truncated in output)...")
    result = test_tool("take_screenshot")
    if result and result.get("success"):
        img_data = result.get("result", {}).get("image_base64", "")
        print(f"Screenshot captured: {len(img_data)} bytes")
    
    # Test 6: Activate Obsidian window
    test_tool("activate_window", {"title_pattern": ".*Obsidian.*"})
    time.sleep(1)
    
    # Test 7: Type text (if Obsidian is open and focused)
    print("\nAttempting to type in Obsidian...")
    test_tool("type_text", {"text": "Hello from Manus! This is a GUI automation test."})
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
