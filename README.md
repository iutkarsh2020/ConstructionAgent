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
3) Install all dependencies from pyproject.toml - USE uv pip install .
4) Run Langgraph studio in local - USE: langgraph dev --config langgraph.json

# Agent Evaluation
## Purpose
The purpose of this document is to design an evaluation strategy for the AI
Powered construction agent. We have divided the overall evaluation into 3 key
areas: Intent Classification, Correctness of Tool Invocation and User Satisfaction
Metrics.

## Strategy
We will create test set of user queries, run them through the agent, and will define
some metrics to evaluate the agent’s performance.

## Evaluation Platforms for AI Agents
### Assumption: We are using and will continue to use the LangChain ecosystem for
our agent development for the foreseeable future.
Before diving into the evaluation process, it's helpful to understand the currently
available real-world solutions. We will assess various platforms based on their
evaluation process—focusing on ease of use, scalability, and modularity—to make
an informed decision for our current and future use cases.

### LangSmith:
### Pros
Part of Langchain Ecosystem, integration with Langgraph Agents will be
easier.
Visually traceable Langchain/ Langgraph runs(Automatically), including
intermediate steps like tool calls, input/outputs to nodes etc.
Capabilities:
- Create test case datasets
- Execute agent testing
- Set up automated evaluation checks
- Gather human feedback
- Perform version comparisons
### Cons
- Paid service
- Needs manual creation of test datasets

### Google Vertex AI Gen AI Evaluation Service:
### Pros
- Support for both final response and trajectory evaluation with six built-in
- metrics (exact match, in-order/any-order, precision, recall, single‑tool use).
- Support for Langgraph agent with additional Vertex AI engine integration.
- Custom metrics via python functions.

### Cons
- Requires google cloud setup with Vertex AI Agent Engine.
- Agent evaluation service and scale features are still in public preview with
limited support.

<img width="367" alt="image" src="https://github.com/user-attachments/assets/3bb90ba0-0d67-4048-89d0-0c03aadb8ea9" /> \

<img width="373" alt="image" src="https://github.com/user-attachments/assets/6d689bc2-69b6-448b-9425-bfdcf841a4f5" />

