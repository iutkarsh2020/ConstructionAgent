import asyncio
from src.agent.core import create_graph

async def main():
    graph = await create_graph()
    return graph

if __name__ == "__main__":
    asyncio.run(main())
