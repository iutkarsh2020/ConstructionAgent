"""
Configuration settings for the Model Control Panel (MCP) client.

This module defines the configuration constants used by the MCP client to connect
to and interact with the tools and prompts servers. It includes:
- Server configurations for tools and prompts
- Required prompt names for the construction agent
"""

# Configuration for MCP client to connect to various servers
MCP_CLIENT_CONFIG = {
    # Configuration for the tools server
    "tools_server": {
        "command": "uv",
        "args": ["run", "src/server/tools.py"],
        "transport": "stdio"
    },
    "prompt_server": {
        "command": "uv",
        "args": ["run", "src/server/prompts.py"],
        "transport": "stdio"
    }
}

# Dictionary mapping internal prompt names to their server-side names
# These prompts are required for the construction agent to function properly
REQUIRED_PROMPT_NAMES = {
    "system_prompt": "system_prompt",
    "query_validation_prompt": "query_validation_prompt",
    "clarification_prompt": "clarification_prompt"
}