"""
MCP Smart Vision Server
HTTP/REST API server for remote desktop control, including pixel-based GUI
automation and element-based UI Automation ("Smart Vision").
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

# Import all tools
from tools import ALL_TOOLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp-remote-control.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="MCP Smart Vision Server",
    description="Remote desktop control with GUI + UI Automation via HTTP API",
    version="3.0.0"
)


def load_api_key() -> str:
    """Load the API key from config.json (falls back to a placeholder)."""
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f).get("api_key", "replace-with-your-generated-key")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Could not read config.json, using placeholder key: {e}")
    return "replace-with-your-generated-key"


# Security configuration — key is read from config.json
API_KEY = load_api_key()


class ToolRequest(BaseModel):
    """Request model for tool execution"""
    parameters: Dict[str, Any] = {}


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from request header"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MCP Smart Vision Server",
        "version": "3.0.0",
        "status": "running",
        "features": ["file_operations", "data_analysis", "organization", "system_control", "gui_automation", "window_management", "smart_vision"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/tools")
async def list_tools(authorized: bool = Header(default=False, alias="X-API-Key")):
    """List all available tools"""
    verify_api_key(authorized)

    tools_list = []
    for tool in ALL_TOOLS:
        tools_list.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool.get("parameters", {})
        })

    return {
        "success": True,
        "tools": tools_list,
        "count": len(tools_list)
    }


@app.post("/api/v1/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    request: ToolRequest,
    x_api_key: Optional[str] = Header(None)
):
    """Execute a specific tool"""
    verify_api_key(x_api_key)

    # Find the tool
    tool = None
    for t in ALL_TOOLS:
        if t["name"] == tool_name:
            tool = t
            break

    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # Execute the tool
    try:
        logger.info(f"Executing tool: {tool_name} with parameters: {request.parameters}")

        # Call the tool function
        result = tool["function"](**request.parameters)

        logger.info(f"Tool {tool_name} completed: {result.get('success', False)}")

        return {
            "success": True,
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


def main():
    """Start the HTTP server"""
    print("=" * 60)
    print("MCP Smart Vision Server v3.0.0")
    print("=" * 60)
    print(f"API Key: {API_KEY}")
    print(f"Total Tools: {len(ALL_TOOLS)}")
    print("\nTool Categories:")
    print("  - File System Operations (9 tools)")
    print("  - Data Analysis (5 tools)")
    print("  - File Organization (4 tools)")
    print("  - System Operations (5 tools)")
    print("  - GUI Automation (9 tools)")
    print("  - Window Management (5 tools)")
    print("  - Smart Vision / UI Automation (4 tools)")
    print("\nStarting server on http://localhost:8080")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()
