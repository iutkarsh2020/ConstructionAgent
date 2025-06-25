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

Since we are working with Langgraph agents, LangSmith is the most suitable and
efficient platform for evaluation. Its tracing capabilities will save us immense
development time, future capabilities will be the most compatible within the same
ecosystem and it will provide the most granular insights into the agent's decision-
making process, especially concerning the "correctness of tool invocation" and
"intent classification accuracy.
"


### Evaluation:
### 1. Intent Classification:
I tried to find different ways to get the most promising results for the MVP. I
considered cosine similarity of vector embeddings, Rule based classification
and LLM based classification and decided to use LLM classification(because
we had to make sure we have enough function arguments along with intent)
for good results and ease of creating an initial working solution.
Dataset:
For the purpose of this assignment, I have manually curated a dataset as can
be seen here(https://smith.langchain.com/public/7e0d0621-6be0-4a8f-aff1-beb04d58f7ac/d).
### Possible intent classifications:
1) "clear_tool_call_measure_area"
2) "clear_tool_call_get_scale"
3) "clear_tool_call_query_pipe_info"
4) "ambiguous_tool_intent"
5) "multiple_tool_intents_with_ambiguity"
6) "multiple_tool_intents_all_clear"
7) "unrelated_query"


### Example dataset: (All expected outputs are classified in one of the above intents)
Input: "Can you tell me the scale of Drawing 101?”
Output: "clear_tool_call_get_scale” (Ground truth)
In production, we can update our datasets from user traces in Langsmith. For each
user run, we can update the inputs and refine the expected outputs.
## Evaluation Strategy:
1. Run the 'Query_Validation’ node from the Langgraph using LangSmith.
2. Use a LLM as a judge for expected and actual outputs from the node.
3. Use custom Evaluators for single test case runs and for summarizations.
4. Use a summarization Evaluator for extracting desired key metrics.
### Metrics(Results): Below are average metrics of 6 runs.
1. Accuracy - 0.85
2. Precision - 0.84
3. Recall - 0.86
4. F1-Score - 0.82

<img width="351" alt="image" src="https://github.com/user-attachments/assets/756489cd-f08d-4b76-a684-f430535e6fd9" />

## 2. Correctness of tool invocation:
### Dataset: I have used the same input dataset as before with the expected output as
graph’s final state, it can be seen here.
Example dataset:
Input: "Can you tell me the scale of Drawing 101?"
Output:
Answer:
final_response: "The scale of Drawing 101 is 1:50.
"
expected_tool_call:
name: "get_scale"
args:
drawing: "Drawing 101"
### Evaluation Strategy:
1. Run the entire graph, use its final state as actual output.
2. Use a LLM as a judge for expected and actual outputs from the node.
3. Use custom Evaluators for single test case runs and for summarizations.
### Metric:
Single tool use: 0.8 (avg of 6 runs)
The evaulation focused only on tool use here. The most critical decision for this
dummy agent is being made at 'Query_Validation’. This node returns a json of
the form:


{
    "intents": [
        {{
        }},
        }},
        {{
        }},
        "unrelated": true | false (True if the query is totally unrelated to the tools you ca
        "tool": "tool_name"
        ,
        "is_ambiguous": true | false, (Tool intent is clear but the required argument is
        "ambiguous_reason": "reason for ambiguity"
        "arguments": {{
        "arg1": "value or null"
        "missing_arguments": ["arg1"]
        "tool": "tool_name"
        ,
        "is_ambiguous": true | false,
        "ambiguous_reason": "reason for ambiguity"
        "arguments": {{
        "arg1": "value"
        "missing_arguments": []
        }}
    ]
}

<img width="369" alt="image" src="https://github.com/user-attachments/assets/08e27adf-c489-4957-9ca6-11f0417496d6" />

### 3. User Satisfaction
We utilize the HEART Framework to evaluate the overall customer satisfaction with
the product.
Happiness
### 1. Customer Satisfaction Score (CSAT):
What it measures: Direct user satisfaction with a specific interaction or
the AI overall.
How to measure: A simple post-interaction survey question: "How
satisfied are you with this interaction?" (e.g., on a scale of 1-5, or with
"Very Satisfied" to "Very Dissatisfied" options). Often presented as a
thumbs up/down.
### Net Promoter Score (NPS):
What it measures: The likelihood of users recommending the AI agent to
others, indicating overall loyalty and satisfaction.

### How to measure: "On a scale of 0-10, how likely are you to recommend [AI
Agent Name] to a friend or colleague?"
Engagement
### Engagement Rate:
What it measures: How often users interact with the AI Agent, or the
average duration of sessions.
How to measure: Number of active users, average session length, number
of messages per user per day/week.
### Adoption
### New User Acquisition Rate / Sign-ups:
What it measures: The number or percentage of new users who create an
account, download the app, or initiate their first session with the AI agent
within a given period.
### How to measure: Track unique user IDs, sign-up forms, or first-time
conversation initiations.
### Activation Rate:
### What it measures: The percentage of new users who complete a defined
"activation event" – a key action that signifies they've experienced the
core value proposition of the AI.
How to measure: Define your activation event (e.g., asking their first
question, completing their first task, interacting with a specific feature).
### Retention
### User Retention / Repeat Usage Rate:
What it measures: The percentage of users who return to use the AI agent
after their initial interaction.
How to measure: Track unique user IDs and their activity over time.
Why it's important: High retention indicates ongoing value and satisfaction.

### Task Completion Rate / Problem Resolution Rate:
What it measures: The percentage of user queries or tasks that the AI
agent successfully handles from start to finish without human intervention
or escalation.
### How to measure: Track sessions where the user's stated goal was met, or
where the conversation ended with a positive outcome (e.g., "Thank you,"
"Yes, that solved it"). Requires clear definition of "completion."
### Retrospection
### What worked well:
LangSmith integration was seamless with LangGraph and made tracing,
debugging, and metric collection very easy. Got into some trouble with llm
API’s rate limits but learnt a lot.
The main NLU task was performed at 'Query_Validation’ node, it returned a
json for intent classification. The rest of the nodes did not rely heavily on
llm calls.
What I would do better the next time:
I would plan better for each node’s output before writing code, design
the graph outputs better for ease during testing and for better results
while testing with Langsmith
