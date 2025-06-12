import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition, ToolNode
load_dotenv()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
class MessagesState(TypedDict):
    messages: Annotated[list[str], add_messages],
    summary: str

async def create_graph():
    client = MultiServerMCPClient({
        "dummy_server": {
            "command": "uv",
            "args": ["run", "mcpserver.py"],
            "transport": "stdio"
        }
    })
    llm = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash', temperature=0, google_api_key = GOOGLE_API_KEY)
    tools = await client.get_tools()

    llm_with_tools = llm.bind_tools(tools)

    sys_prompt = SystemMessage(await client.get_system_prompt(server_name="dummy_server", prompt_name="system_prompt"))

    # we can add a conditional loop here after human query, to give human options to make prompt less ambiguous
    def human_input(state: MessagesState):
        user_query = input('Enter your query: ')
        return {'messages': [HumanMessage(content=user_query)]}
    
    def agent_call(state: MessagesState):
        
    builder = StateGraph(MessagesState)

    builder.add_node('Human', human_input)
    builder.add_node('Agent', agent_call)
    builder.add_node('tools', ToolNode(tools))
    # LOGIC
    builder.add_edge(START, 'Human')
    builder.add_edge('Human', 'Agent')
    builder.add_conditional_edges('Agent', tools_condition)
    builder.add_edge('tools', 'Human')