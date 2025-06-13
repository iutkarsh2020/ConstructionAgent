# graph_loader.py
import asyncio
from agent.core import AgentGraph

# Run the async builder synchronously and expose the compiled graph
agent_graph = AgentGraph()
asyncio.run(agent_graph.build_graph())
graph = agent_graph.graph