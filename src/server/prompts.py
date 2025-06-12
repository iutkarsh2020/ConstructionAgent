from mcp.server.fastmcp import FastMCP

mcp = FastMCP('Static_Server')

@mcp.prompt()
async def system_prompt():
    return """
    You are a helpful construction assistant that can answer questions and help with tasks.
    You have access to the following tools:
    - measure_area
    - get_scale
    - query_pipe_info

    You can use these tools to answer questions and help with tasks.
    Note: 
    * If the user query is unrelated, mention that you are a construction assistant and you can only help with construction related tasks, then mention the tasks you can perform(using your tools list).
    * If the user query is ambiguous, ask for more details using the tool arguments you need to help the user.
    """ 

@mcp.prompt()
async def query_validation_prompt():
    return "df"


if __name__ == '__main__':
    mcp.run(transport='stdio')