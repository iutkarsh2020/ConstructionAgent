from agent.core import create_graph
import asyncio

async def main():
    
    d = await create_graph()
    print(d)

if __name__ == "__main__":
    asyncio.run(main())








