from src.agent.core import AgentGraph
import asyncio
from langchain_core.messages import HumanMessage

async def run():
    agent_graph = AgentGraph()
    await agent_graph.build_graph()
    graph = agent_graph.graph

    thread_config = {'configurable': {'thread_id': '1'}}
    result = await graph.ainvoke({'messages':[HumanMessage(content="What is area of drawing A?")]}, config=thread_config)
    print(result)






