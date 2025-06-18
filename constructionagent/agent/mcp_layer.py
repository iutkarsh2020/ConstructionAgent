"""
Model Context Protocol (MCP) Layer for managing tools and prompts.

This module provides an interface to interact with the MCP server, which manages
the tools and prompts used by the construction agent. It handles:
- Tool retrieval and caching
- Prompt management and caching
- Server communication through MultiServerMCPClient
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from constructionagent.agent.mcp_config import MCP_CLIENT_CONFIG

class MCPLayer:
    """
    Layer for interacting with the Model Control Panel (MCP) server.
    
    This class manages the communication with MCP servers to:
    1. Fetch and cache available tools
    2. Manage and cache prompts
    3. Provide easy access to tools and prompts by name
    
    The layer implements caching to minimize server requests and improve
    performance.
    """

    def __init__(self):
        """
        Initialize the MCP layer with a client connection.
        
        Sets up:
        - MCP client connection using configuration
        - Tools cache (initialized as None)
        - Prompts cache (initialized as empty dict)
        """
        self.client = MultiServerMCPClient(MCP_CLIENT_CONFIG)
        self.tools = None
        self.prompts = {}

    async def fetch_tools(self):
        """
        Fetch available tools from the MCP server.
        
        Returns:
            list: List of available tools
            
        Note:
            Tools are cached after first fetch to minimize server requests
        """
        if not self.tools:
            self.tools = await self.client.get_tools()
        return self.tools

    async def fetch_prompt(self, prompt_name: str, server_name: str = "prompt_server"):
        """
        Fetch a single prompt from the MCP server.
        
        Args:
            prompt_name (str): Name of the prompt to fetch
            server_name (str, optional): Name of the MCP server. Defaults to "prompt_server"
            
        Returns:
            Prompt: The fetched prompt object
            
        Note:
            Fetched prompts are cached in the prompts dictionary
        """
        prompt = await self.client.get_prompt(server_name=server_name, prompt_name=prompt_name)
        self.prompts[prompt_name] = prompt
        return prompt

    async def fetch_prompts(self, prompt_names: list[str], server_name: str = "prompt_server"):
        """
        Fetch multiple prompts from the MCP server.
        
        Args:
            prompt_names (list[str]): List of prompt names to fetch
            server_name (str, optional): Name of the MCP server. Defaults to "prompt_server"
            
        Returns:
            dict: Dictionary of prompt names to prompt objects
            
        Note:
            - Prompts are fetched only if not already cached
            - All fetched prompts are cached for future use
        """
        if not self.prompts:
            for name in prompt_names:
                prompt = await self.fetch_prompt(name, server_name=server_name)
                self.prompts[name] = prompt
        return self.prompts

    def get_tool(self, name: str):
        """
        Retrieve a specific tool by name from the cached tools.
        
        Args:
            name (str): Name of the tool to retrieve
            
        Returns:
            Tool or None: The requested tool if found, None otherwise
            
        Note:
            Returns None if tools haven't been fetched yet
        """
        if self.tools is None:
            return None
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_prompt(self, name):
        """
        Retrieve a specific prompt by name from the cached prompts.
        
        Args:
            name (str): Name of the prompt to retrieve
            
        Returns:
            Prompt or None: The requested prompt if found, None otherwise
        """
        return self.prompts.get(name) 
