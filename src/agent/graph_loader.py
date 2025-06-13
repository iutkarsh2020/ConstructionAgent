"""
Graph loader module for initializing the construction agent's conversation graph.

This module provides a synchronous interface to initialize and load the agent's
conversation graph. It handles the asynchronous setup of the graph and exposes
the compiled graph for use in the application.

The module is designed to be imported by other parts of the application that need
access to the agent's conversation graph.
"""

import asyncio
from src.agent.core import AgentGraph

_agent_instance = AgentGraph()

async def graph():
    """
    Asynchronously builds and returns the compiled LangGraph instance.

    This function ensures that the AgentGraph's asynchronous setup
    (like fetching tools and prompts) is completed before the graph
    is returned. It's designed to be called by an asynchronous context,
    such as the `langgraph dev` server.

    Returns:
        langgraph.graph.CompiledGraph: The fully initialized and compiled graph.
    """
    if _agent_instance.graph is None:
        # Build the graph only once if it hasn't been built yet
        print("Building AgentGraph for the first time...")
        await _agent_instance.build_graph()
        print("AgentGraph built successfully.")
    return _agent_instance.graph