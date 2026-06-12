"""
Tunnel Manager for MCP Remote Desktop Control
Handles ngrok tunnel creation and management.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

try:
    from pyngrok import ngrok, conf
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False
    logging.warning("pyngrok not installed. Tunnel features will be disabled.")

logger = logging.getLogger(__name__)


class TunnelManager:
    """Manages ngrok tunnel for remote access."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.tunnel = None
        self.public_url = None
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ngrok(self, auth_token: Optional[str] = None) -> bool:
        """Setup ngrok with authentication token."""
        if not NGROK_AVAILABLE:
            logger.error("pyngrok is not installed")
            return False
        
        # Get auth token from parameter, config, or environment
        token = auth_token or self.config.get("ngrok_auth_token") or os.environ.get("NGROK_AUTH_TOKEN")
        
        if not token:
            logger.error("No ngrok auth token provided")
            return False
        
        try:
            # Set ngrok auth token
            ngrok.set_auth_token(token)
            
            # Save token to config
            self.config["ngrok_auth_token"] = token
            self._save_config()
            
            logger.info("ngrok authentication configured successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to setup ngrok: {str(e)}")
            return False
    
    def start_tunnel(self, port: int = 8080, auth_token: Optional[str] = None) -> Optional[str]:
        """Start ngrok tunnel."""
        if not NGROK_AVAILABLE:
            logger.error("pyngrok is not installed. Install with: pip install pyngrok")
            return None
        
        # Setup ngrok if auth token provided
        if auth_token:
            if not self.setup_ngrok(auth_token):
                return None
        
        try:
            # Start tunnel
            logger.info(f"Starting ngrok tunnel on port {port}...")
            self.tunnel = ngrok.connect(port, bind_tls=True)
            self.public_url = self.tunnel.public_url
            
            logger.info(f"✅ Tunnel established!")
            logger.info(f"Public URL: {self.public_url}")
            
            return self.public_url
        
        except Exception as e:
            logger.error(f"Failed to start tunnel: {str(e)}")
            return None
    
    def stop_tunnel(self):
        """Stop ngrok tunnel."""
        if self.tunnel:
            try:
                ngrok.disconnect(self.tunnel.public_url)
                logger.info("Tunnel stopped")
                self.tunnel = None
                self.public_url = None
            except Exception as e:
                logger.error(f"Error stopping tunnel: {str(e)}")
    
    def get_public_url(self) -> Optional[str]:
        """Get the current public URL."""
        return self.public_url
    
    def is_active(self) -> bool:
        """Check if tunnel is active."""
        return self.tunnel is not None


def main():
    """Test tunnel manager."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tunnel_manager.py <ngrok_auth_token> [port]")
        print("\nGet your free ngrok auth token at: https://dashboard.ngrok.com/get-started/your-authtoken")
        sys.exit(1)
    
    auth_token = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    
    manager = TunnelManager()
    public_url = manager.start_tunnel(port, auth_token)
    
    if public_url:
        print(f"\n{'='*60}")
        print("Tunnel Active!")
        print(f"{'='*60}")
        print(f"Public URL: {public_url}")
        print(f"Local Port: {port}")
        print(f"\nPress Ctrl+C to stop the tunnel...")
        print(f"{'='*60}\n")
        
        try:
            input()  # Keep running
        except KeyboardInterrupt:
            print("\nStopping tunnel...")
            manager.stop_tunnel()
    else:
        print("Failed to start tunnel")
        sys.exit(1)


if __name__ == "__main__":
    main()
