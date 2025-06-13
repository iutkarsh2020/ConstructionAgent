from agent.core import create_graph
import asyncio

def get_tool_descriptions(tools):
    descriptions = []

    for tool in tools:
        tool_name = tool.name
        description = tool.description.strip().split("\n")[0]  # First line only
        args = tool.args_schema.get('properties', {})
        required_args = tool.args_schema.get('required', [])

        arg_list = []
        for arg in required_args:
            arg_type = args.get(arg, {}).get("type", "string")
            arg_list.append(f"{arg}: {arg_type}")

        arg_string = ", ".join(arg_list)
        full_description = f"{tool_name}({arg_string}) → {description}"
        descriptions.append(full_description)

    return "\n".join(f"{i+1}.{d}" for i, d in enumerate(descriptions))
async def main():
    
    graph, tools, prompts = await create_graph()
    # filtered_tools = get_tool_descriptions(tools)
    # print(filtered_tools)

if __name__ == "__main__":
    asyncio.run(main())





