import sys
import os
import platform
import subprocess
import socket
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHeader("debug_install.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DebugLogger")

def check_system():
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Working Directory: {os.getcwd()}")

def check_dependencies():
    deps = ["pyautogui", "pywinauto", "fastapi", "uvicorn", "requests", "ngrok"]
    for dep in deps:
        try:
            __import__(dep)
            logger.info(f"Dependency {dep}: INSTALLED")
        except ImportError:
            logger.error(f"Dependency {dep}: MISSING")

def check_network():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        logger.info("Network: CONNECTED")
    except Exception as e:
        logger.error(f"Network: FAILED ({e})")

if __name__ == "__main__":
    logger.info("=== MCP Server Debug Session Started ===")
    check_system()
    check_network()
    check_dependencies()
    logger.info("=== Debug Session Finished ===")
