import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path

from agent.state import MessagesState

load_dotenv()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

async def create_graph():
    client = MultiServerMCPClient({
        "tools_server": {
            "command": "python",
            "args": [str(PROJECT_ROOT / "src" / "server" / "tools.py")],
            "transport": "stdio"
        },
        "prompt_server": {
            "command": "python",
            "args": [str(PROJECT_ROOT / "src" / "server" / "prompts.py")],
            "transport": "stdio"
        }
    })
    llm = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash', temperature=0, google_api_key = GOOGLE_API_KEY)
    tools = await client.get_tools(server_name="tools_server")

    for tool in tools:
        print(tool)
        print("--------------------------------")
    llm_with_tools = llm.bind_tools(tools)
    
    sys_prompt = SystemMessage(str(await client.get_prompt(server_name="prompt_server", prompt_name="system_prompt")))
    query_validation_prompt = await client.get_prompt(server_name="prompt_server", prompt_name="query_validation_prompt")
    def intent_and_slot_validator(state: MessagesState):
        user_query = input('Enter your query: ')
        return {'messages': [HumanMessage(content=user_query)]}
    
    def agent_call(state: MessagesState):
        # summary will help reducing token count
        return {'messages': llm_with_tools.invoke([sys_prompt] + [state['summary']] + state['messages'])}

    builder = StateGraph(MessagesState)

    builder.add_node('Query Validator', intent_and_slot_validator)
    builder.add_node('Agent', agent_call)
    builder.add_node('tools', ToolNode(tools))
    # LOGIC
    builder.add_edge(START, 'Query Validator')
    builder.add_edge('Query Validator', 'Agent')
    builder.add_conditional_edges('Agent', tools_condition)
    builder.add_edge('tools', 'Query Validator')

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return (graph, tools, [sys_prompt, query_validation_prompt])