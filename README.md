# MCP Smart Vision Server

**An HTTP/REST control server that gives an AI agent eyes and hands on a Windows desktop.**

This server exposes your machine's filesystem, data tools, system commands, and — most importantly — **full GUI automation** over a simple authenticated REST API. It started as a way to let an autonomous agent (e.g. an [OpenClaw](https://github.com/) / LLM-driven assistant) actually *operate* a Windows PC: take screenshots, move the mouse, type, manage windows, and click UI elements by name.

It supports two styles of automation:

- **Pixel-based** (`pyautogui`) — move/click at coordinates, type text, press hotkeys, capture the screen.
- **Element-based "Smart Vision"** (`pywinauto` + Windows UI Automation) — *inspect* an app's real UI tree and click a button or fill a field **by its name**, no coordinates required. This is faster and survives windows being moved or resized. See [`architecture.md`](architecture.md).

> ⚠️ **This is a remote-control tool.** When run with `--tunnel` it exposes control of your desktop to anyone who has the public URL **and** the API key. Read the [Security](#security) section before exposing it to the internet.

---

## Features

**41 tools** across 7 categories:

| Category | Tools | Examples |
| --- | --- | --- |
| 🗂️ **File System** (9) | list, read, write, delete, move, copy, mkdir, file info, search | `read_file`, `move_file`, `search_files` |
| 📊 **Data Analysis** (5) | analyze CSV/Excel, query with pandas, merge datasets, export, stats | `analyze_data`, `query_data` |
| 🧹 **Organization** (4) | organize by type/date, find duplicates, bulk rename, smart sort | `organize_files`, `find_duplicates` |
| ⚙️ **System** (5) | run shell commands, disk usage, system info, env vars, processes | `execute_command`, `system_info` |
| 🖱️ **GUI Automation** (9) | screenshot, move/click mouse, type, press key, hotkey, scroll, screen size | `take_screenshot`, `click_mouse`, `type_text` |
| 🪟 **Window Management** (5) | list/find/activate windows, read window text, click buttons | `list_windows`, `activate_window` |
| 👁️ **Smart Vision / UI Automation** (4) | inspect UI tree, click element by name, set field value, read element text | `inspect_window`, `click_ui_element` |

---

## Requirements

- **Windows 10/11** (the GUI + UI Automation tools are Windows-specific)
- **Python 3.10+**
- A free **[ngrok](https://dashboard.ngrok.com/get-started/your-authtoken)** account — only if you want remote access via `--tunnel`

---

## Installation

```bash
# 1. Clone
git clone https://github.com/IsaiahAnson/mcp-smart-vision.git
cd mcp-smart-vision

# 2. (Recommended) create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

Or just run the bundled installer:

```bash
install.bat
```

### Configure

Copy the example config and fill in your own values:

```bash
copy config.example.json config.json
```

```jsonc
{
  "api_key": "replace-with-your-generated-key",  // any strong secret string
  "host": "127.0.0.1",
  "port": 8080,
  "enable_tunnel": false,
  "ngrok_auth_token": null,                       // only needed for --tunnel
  "allowed_ips": [],
  "rate_limit": { "requests_per_minute": 60 }
}
```

> 🔒 `config.json` is **git-ignored** on purpose — it holds your API key and ngrok token. Never commit it.

If you don't create one, `start_server.py` will generate a `config.json` with a random `api_key` on first run.

Security behavior:

- The server **refuses every authenticated request** (HTTP 503) until `api_key` is set to a real
  secret of at least 24 characters. The placeholder value above is rejected, so a missing or
  unedited config can never leave the machine controllable.
- API keys are compared in constant time.
- `allowed_ips`: when non-empty, only these client IPs (plus localhost) may connect. Over the
  ngrok tunnel the original client IP from `X-Forwarded-For` is used.
- `rate_limit.requests_per_minute`: per-client-IP limit (HTTP 429 when exceeded). Set to 0 to disable.
- The server binds to `host` (default `127.0.0.1`). Tunnel mode also binds to loopback, since ngrok
  forwards to localhost.

---

## Running the server

### Local only (safe default)

```bash
python start_server.py --local
```

Server runs at `http://127.0.0.1:8080`. Interactive API docs are available at `http://127.0.0.1:8080/docs`.

### With a public ngrok tunnel (remote access)

```bash
# First time: save your ngrok token
python start_server.py --setup-ngrok YOUR_NGROK_TOKEN

# Then start with the tunnel
python start_server.py --tunnel
```

On startup it prints the **Public URL** and **API Key** you'll use from the client side.

---

## API usage

All tool calls are `POST /api/v1/tools/{tool_name}` with a JSON body of `{"parameters": {...}}` and your key in the `X-API-Key` header.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Server info |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/tools` | List every available tool + its schema |
| `POST` | `/api/v1/tools/{tool_name}` | Execute a tool |

### Example: take a screenshot

```python
import requests

BASE = "http://127.0.0.1:8080/api/v1"
HEADERS = {"X-API-Key": "your-api-key", "Content-Type": "application/json"}

r = requests.post(f"{BASE}/tools/take_screenshot", headers=HEADERS, json={"parameters": {}})
print(r.json())
```

### Example: pixel-based — type into the active window

```python
requests.post(f"{BASE}/tools/type_text", headers=HEADERS,
              json={"parameters": {"text": "# New Note\n\nHello from the agent"}})

requests.post(f"{BASE}/tools/hotkey", headers=HEADERS,
              json={"parameters": {"keys": ["ctrl", "s"]}})  # save
```

### Example: Smart Vision — click a button *by name* (no coordinates)

```python
# 1. See what's actually in the window
requests.post(f"{BASE}/tools/inspect_window", headers=HEADERS,
              json={"parameters": {"title_re": ".*Obsidian.*"}})

# 2. Click an element by its label
requests.post(f"{BASE}/tools/click_ui_element", headers=HEADERS,
              json={"parameters": {"window_title": ".*Obsidian.*",
                                   "element_name": "Create new note"}})

# 3. Fill a text field directly
requests.post(f"{BASE}/tools/set_ui_element_value", headers=HEADERS,
              json={"parameters": {"window_title": ".*Settings.*",
                                   "element_name": "Search",
                                   "value": "appearance"}})
```

Discover every tool and its parameters at runtime with `GET /api/v1/tools`.

---

## Security

This server can read your files and fully control your desktop. Treat it accordingly:

- **API key auth** — every request must send a valid `X-API-Key`. Use a long random string.
- **Start local.** Only use `--tunnel` when you genuinely need remote access, and shut it down when you're done.
- **The tunnel is public.** Anyone with the ngrok URL + API key can control your machine. Don't share them, and rotate the key if leaked.
- **`config.json` is git-ignored** so your key and ngrok token never get committed. Double-check before pushing.
- **Run with the least privilege** needed; only run as administrator if a specific automation requires it.

### Built-in safety

- **PyAutoGUI failsafe** — slam your mouse into any screen corner to abort all automation instantly.
- **Action pause** — a short default delay between automated actions to prevent runaway input.
- **Activity logging** — all tool calls are written to `mcp-remote-control.log` (git-ignored).

---

## Project structure

```
mcp-smart-vision/
├── http_server.py        # FastAPI app: auth, tool dispatch, REST endpoints
├── start_server.py       # Launcher: --local / --tunnel / --setup-ngrok
├── tunnel_manager.py     # ngrok tunnel lifecycle (pyngrok)
├── debug_logger.py       # Verbose logging helper
├── test_gui.py           # Smoke test for the GUI automation tools
├── config.example.json   # Copy to config.json and fill in
├── requirements.txt
├── install.bat
├── architecture.md       # Smart Vision (UI Automation) design notes
└── tools/
    ├── filesystem.py         # File System tools
    ├── data.py               # Data Analysis tools
    ├── organize.py           # Organization tools
    ├── system.py             # System tools
    ├── gui_automation.py     # Pixel-based GUI tools
    ├── window_automation.py  # Window management tools
    └── uia_automation.py     # Smart Vision / UI Automation tools
```

---

## Troubleshooting

- **`pyngrok not installed` / tunnel disabled** → `pip install pyngrok` (it's in `requirements.txt`).
- **GUI automation does nothing** → ensure target windows are visible (not minimized); some apps block synthetic input; try running elevated.
- **Smart Vision can't find an element** → run `inspect_window` first to get the exact element names; use regex for `window_title` (e.g. `".*Notepad.*"`).
- **401 Invalid API key** → the `X-API-Key` header must match `api_key` in `config.json`.

---

## Tests

```bash
pip install fastapi httpx pytest
pytest tests
```

The suite covers API-key enforcement, rate limiting and the IP allowlist, using a stub tools module
so it runs on any OS.

## License

Copyright (c) 2026 Isaiah Anson. All rights reserved. You may use the released software for
personal, non-commercial use; copying, modifying or redistributing it requires written
permission. See [LICENSE](LICENSE).


## Built with

[FastAPI](https://fastapi.tiangolo.com/) · [PyAutoGUI](https://pyautogui.readthedocs.io/) · [pywinauto](https://pywinauto.readthedocs.io/) · [pyngrok](https://pyngrok.readthedocs.io/) · [pandas](https://pandas.pydata.org/)
