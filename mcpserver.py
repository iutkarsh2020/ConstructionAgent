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


if __name__ == '__main__':
    mcp.run()

