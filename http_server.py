"""
MCP Smart Vision Server
HTTP/REST API server for remote desktop control, including pixel-based GUI
automation and element-based UI Automation ("Smart Vision").
"""

import json
import logging
import secrets
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Request
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


PLACEHOLDER_API_KEY = "replace-with-your-generated-key"
MIN_API_KEY_LENGTH = 24
LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}


def load_config() -> Dict[str, Any]:
    """Load config.json, or return an empty dict if it is missing or unreadable."""
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Could not read config.json: {e}")
    return {}


CONFIG = load_config()


def load_api_key(config: Dict[str, Any]) -> Optional[str]:
    """Return the configured API key, or None if it is missing, the public
    placeholder, or too short. Without a real key every authenticated request
    is refused, so a missing config can never leave the machine controllable
    with the placeholder key printed in the README."""
    key = config.get("api_key")
    if not isinstance(key, str) or key == PLACEHOLDER_API_KEY or len(key) < MIN_API_KEY_LENGTH:
        logger.error(
            "No valid api_key in config.json (missing, placeholder, or shorter than "
            f"{MIN_API_KEY_LENGTH} characters). All authenticated requests will be refused. "
            "Run start_server.py once to generate a config with a random key."
        )
        return None
    return key


# Security configuration — read from config.json
API_KEY = load_api_key(CONFIG)
ALLOWED_IPS = set(CONFIG.get("allowed_ips") or [])
REQUESTS_PER_MINUTE = int((CONFIG.get("rate_limit") or {}).get("requests_per_minute", 60))

_request_times: Dict[str, deque] = defaultdict(deque)
_rate_lock = threading.Lock()


def client_ip(request: Request) -> str:
    """Best-effort client IP. Requests arriving over the ngrok tunnel reach the
    server from loopback, so the forwarded header is trusted only in that case."""
    direct = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and direct in LOOPBACK_HOSTS:
        return forwarded.split(",")[0].strip()
    return direct


@app.middleware("http")
async def enforce_ip_allowlist_and_rate_limit(request: Request, call_next):
    """Apply config.json's allowed_ips and rate_limit to every request."""
    ip = client_ip(request)

    if ALLOWED_IPS and ip not in ALLOWED_IPS and ip not in LOOPBACK_HOSTS:
        logger.warning(f"Rejected request from non-allowlisted IP {ip}")
        return JSONResponse(status_code=403, content={"error": "IP not allowed"})

    if REQUESTS_PER_MINUTE > 0:
        now = time.monotonic()
        with _rate_lock:
            window = _request_times[ip]
            while window and now - window[0] > 60:
                window.popleft()
            if len(window) >= REQUESTS_PER_MINUTE:
                return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})
            window.append(now)

    return await call_next(request)


class ToolRequest(BaseModel):
    """Request model for tool execution"""
    parameters: Dict[str, Any] = {}


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from request header (constant-time comparison)."""
    if API_KEY is None:
        raise HTTPException(status_code=503, detail="Server has no valid API key configured")
    if not x_api_key or not secrets.compare_digest(x_api_key.encode(), API_KEY.encode()):
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
async def list_tools(x_api_key: Optional[str] = Header(None)):
    """List all available tools"""
    verify_api_key(x_api_key)

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
        logger.info(f"Executing tool: {tool_name} with parameters: {sorted(request.parameters)}")

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
    if API_KEY is None:
        print("ERROR: no valid api_key in config.json. Run start_server.py to generate one.")
        sys.exit(1)
    host = CONFIG.get("host", "127.0.0.1")
    port = int(CONFIG.get("port", 8080))
    print(f"Total Tools: {len(ALL_TOOLS)}")
    print("\nTool Categories:")
    print("  - File System Operations (9 tools)")
    print("  - Data Analysis (5 tools)")
    print("  - File Organization (4 tools)")
    print("  - System Operations (5 tools)")
    print("  - GUI Automation (9 tools)")
    print("  - Window Management (5 tools)")
    print("  - Smart Vision / UI Automation (4 tools)")
    print(f"\nStarting server on http://{host}:{port}")
    print("=" * 60)

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
