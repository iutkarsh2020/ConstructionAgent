# Construction Agent AI
This is a dummy construction agent, which can answer user queries relating a drawing.


### Key Features & Supported Queries
Supported Tools:
    measure_area(region): returns area of a specified region
    get_scale(drawing): returns scale used in a drawing
    query_pipe_info(location):  returns information about a water pipe at a specified location


TO RUN THE AGENT ON LANGGRAPH STUDIO(local):
1) In the root directory, create a new VM - USE: uv venv
2) Activate newly creatd VM - USE: source ./venv/bin/activate
3) Install all dependencies from pyproject.toml - USE python install .
4) Run Langgraph studio in local - USE: langgraph dev --config langgraph.json