from agent.core import create_graph
import asyncio


async def main():
    
    graph, tools, sys_prompt, query_validation_prompt = await create_graph()
    # filtered_tools = get_tool_descriptions(tools)
    # print(filtered_tools)

if __name__ == "__main__":
    asyncio.run(main())





