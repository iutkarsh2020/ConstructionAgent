import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from agent.mcp_config import MCP_CLIENT_CONFIG

class MCPLayer:
    def __init__(self):
        self.client = MultiServerMCPClient(MCP_CLIENT_CONFIG)
        self.tools = None
        self.prompts = {}

    async def fetch_tools(self):
        if not self.tools:
            self.tools = await self.client.get_tools()
        return self.tools

    async def fetch_prompt(self, prompt_name: str, server_name: str = "prompt_server"):
        prompt = await self.client.get_prompt(server_name=server_name, prompt_name=prompt_name)
        self.prompts[prompt_name] = prompt
        return prompt

    async def fetch_prompts(self, prompt_names: list[str], server_name: str = "prompt_server"):
        if not self.prompts:
            for name in prompt_names:
                prompt = await self.fetch_prompt(name, server_name=server_name)
                self.prompts[name] = prompt
        return self.prompts

    def get_tool(self, name: str):
        if self.tools is None:
            return None
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_prompt(self, name):
        return self.prompts.get(name) 