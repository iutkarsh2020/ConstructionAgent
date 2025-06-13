from agent.core import AgentGraph
import asyncio
from langchain_core.messages import HumanMessage

async def main():
    agent_graph = AgentGraph()
    await agent_graph.build_graph()
    graph = agent_graph.graph

    thread_config = {'configurable': {'thread_id': '1'}}
    result = await graph.ainvoke({'messages':[HumanMessage(content="What is the area of region A and scale of drawing V?")]}, config=thread_config)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())





