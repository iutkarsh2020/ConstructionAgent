MCP_CLIENT_CONFIG = {
    "tools_server": {
        "command": "uv",
        "args": ["run", "server/tools.py"],
        "transport": "stdio"
    },
    "prompt_server": {
        "command": "uv",
        "args": ["run", "server/prompts.py"],
        "transport": "stdio"
    }
}