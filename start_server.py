"""
MCP Remote Desktop Control - Server Launcher
Starts the HTTP server with optional ngrok tunnel.
"""

import os
import sys
import json
import time
import secrets
import logging
import threading
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_or_create_config():
    """Load or create configuration file."""
    config_file = Path(__file__).parent / "config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {
            "api_key": secrets.token_urlsafe(32),
            "host": "127.0.0.1",
            "port": 8080,
            "enable_tunnel": False,
            "ngrok_auth_token": None
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    return config


def start_with_tunnel(config):
    """Start server with ngrok tunnel."""
    from tunnel_manager import TunnelManager
    import uvicorn
    from http_server import app
    
    port = config.get("port", 8080)
    ngrok_token = config.get("ngrok_auth_token")
    
    if not ngrok_token:
        logger.error("No ngrok auth token found in config!")
        logger.info("Get your free token at: https://dashboard.ngrok.com/get-started/your-authtoken")
        logger.info("Then add it to config.json or set NGROK_AUTH_TOKEN environment variable")
        return
    
    # Start tunnel in background
    tunnel_manager = TunnelManager()
    
    def start_tunnel_thread():
        time.sleep(2)  # Wait for server to start
        public_url = tunnel_manager.start_tunnel(port, ngrok_token)
        if public_url:
            print("\n" + "="*70)
            print("🌐 REMOTE ACCESS ENABLED")
            print("="*70)
            print(f"Public URL: {public_url}")
            print(f"API Key:    {config['api_key']}")
            print("="*70)
            print("\nShare these credentials to enable remote control!")
            print("The server will remain running until you press Ctrl+C\n")
    
    tunnel_thread = threading.Thread(target=start_tunnel_thread, daemon=True)
    tunnel_thread.start()
    
    # Start server. Bind to loopback only: ngrok forwards to localhost, so there
    # is no reason to also expose the server to every machine on the LAN.
    logger.info(f"Starting server on 127.0.0.1:{port}...")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


def start_local_only(config):
    """Start server for local access only."""
    import uvicorn
    from http_server import app
    
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 8080)
    
    print("\n" + "="*70)
    print("🖥️  LOCAL SERVER MODE")
    print("="*70)
    print(f"Server URL: http://{host}:{port}")
    print(f"API Key:    {config['api_key']}")
    print(f"API Docs:   http://{host}:{port}/docs")
    print("="*70)
    print("\nServer is running locally only (no remote access)")
    print("Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=host, port=port, log_level="info")


def main():
    """Main entry point."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║         MCP Remote Desktop Control Server v2.0                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Load configuration
    config = load_or_create_config()
    
    # Check if tunnel should be enabled
    enable_tunnel = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--tunnel":
            enable_tunnel = True
        elif sys.argv[1] == "--local":
            enable_tunnel = False
        elif sys.argv[1] == "--setup-ngrok":
            if len(sys.argv) < 3:
                print("Usage: python start_server.py --setup-ngrok <auth_token>")
                print("\nGet your free token at: https://dashboard.ngrok.com/get-started/your-authtoken")
                sys.exit(1)
            
            config["ngrok_auth_token"] = sys.argv[2]
            with open(Path(__file__).parent / "config.json", 'w') as f:
                json.dump(config, f, indent=2)
            print("✅ ngrok auth token saved to config.json")
            print("Now run: python start_server.py --tunnel")
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("""
Usage: python start_server.py [OPTIONS]

Options:
  --local           Start server for local access only (default)
  --tunnel          Start server with ngrok tunnel for remote access
  --setup-ngrok     Save ngrok auth token to config
  --help            Show this help message

Examples:
  python start_server.py --local
  python start_server.py --setup-ngrok YOUR_NGROK_TOKEN
  python start_server.py --tunnel

Get ngrok token: https://dashboard.ngrok.com/get-started/your-authtoken
""")
            sys.exit(0)
    
    # Start server
    try:
        if enable_tunnel:
            start_with_tunnel(config)
        else:
            start_local_only(config)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
