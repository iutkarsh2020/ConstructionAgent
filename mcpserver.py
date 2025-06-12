# This will generate our MCP server

from mcp.server.fastmcp import FastMCP

mcp = FastMCP('Static_Server')

@mcp.tool()
def measure_area(region):
    ''' Measures area of a specified region
    Args:
    Region: A region from the drawing
    '''
    return f"100"

@mcp.tool()
def get_scale(drawing):
    ''' Fetches the scale used in a drawing
    Args:
    drawing: A drawing object
    '''
    # drawing processing steps
    scale = 'meter'
    return scale


@mcp.tool()
def query_pipe_info(location):
    '''
    Returns information about a water pipe at a specified location.

    Args:
    location: A location in the drawing

    Returns:
    A dictionary containing attributes about the pipe, such as:
      - pipe_id
      - diameter
      - length
      - installation_date
      - last_inspection_date
      - condition
    '''
    pipe_information = {
        "pipe_id": "WP-1023",
        "diameter": "300 mm",
        "length": "45.7 meters",
        "installation_date": "2015-06-23",
        "last_inspection_date": "2024-12-15",
        "condition": "Good"
    }

    return pipe_information

@mcp.prompt()
def system_prompt():
    return """
    You are a helpful construction assistant that can answer questions and help with tasks.
    You have access to the following tools:
    - measure_area
    - get_scale
    - query_pipe_info

    You can use these tools to answer questions and help with tasks.
    Note: 
    * If the user query is unrelated, mention that you are a construction assistant and you can only help with construction related tasks.
    * If the user query is ambiguous, ask for more details using the tool arguments you need to help the user.
    """


if __name__ == '__main__':
    mcp.run()

