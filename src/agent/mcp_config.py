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

REQUIRED_PROMPT_NAMES = {
    "system_prompt": "system_prompt",
    "query_validation_prompt": "query_validation_prompt",
    "clarification_prompt": "clarification_prompt"
}