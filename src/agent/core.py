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
            "command": "uv",
            "args": ["run", "server/tools.py"],
            "transport": "stdio"
        },
        "prompt_server": {
            "command": "uv",
            "args": ["run", "server/prompts.py"],
            "transport": "stdio"
        }
    })
    llm = ChatGoogleGenerativeAI(model = 'gemini-2.0-flash', temperature=0, google_api_key = GOOGLE_API_KEY)
    tools = await client.get_tools()

    llm_with_tools = llm.bind_tools(tools)
    
    sys_prompt = await client.get_prompt(server_name="prompt_server", prompt_name="system_prompt")
    query_validation_prompt = await client.get_prompt(server_name="prompt_server", prompt_name="query_validation_prompt")

    async def get_tool_descriptions(tools):
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
    
    # we can add a conditional loop here after human query, to give human options to make prompt less ambiguous
    async def intent_and_slot_validator(state: MessagesState):
        user_query = state['messages'][-1]
        tool_descriptions = get_tool_descriptions(tools)
        validation_sys_message = SystemMessage(
            content=query_validation_prompt[0].content.format(tool_descriptions=tool_descriptions)
        )
        result = await llm_with_tools.ainvoke([validation_sys_message, user_query])
        return {'messages': [result]}

    async def agent_call(state: MessagesState):
        query = state['messages'][-1]
        if isinstance(query, ToolMessage):
            print(query)
            result = await llm_with_tools.ainvoke(state['messages'])
            return {'messages': [result]}
        try:
            query = query.content.strip('```json\n').strip('```')
            query = json.loads(query)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        print()
        if query.get("unrelated", 'true'):
            return {
                "messages": [
                    AIMessage(content="Sorry, the query seems unfamiliar. I am a construction assistant and I can only help with construction related tasks.")
                ]
            }
        intents = query.get("intents", [])
        ambiguous_intents = [intent for intent in intents if intent["is_ambiguous"]]

        if ambiguous_intents:
            clarification_prompt = SystemMessage(content="""
            You're a helpful assistant. A user query was mapped to one or more tool calls, but some tools couldn't be used due to missing arguments.
            
            Your job is to:
            1. Read the JSON list of ambiguous tool intents.
            2. For each, clearly explain what is missing.
            3. Then ask the user nicely to provide that missing information.
            Respond as a friendly assistant — not in JSON — just plain language.
            """)
    
            human_message = HumanMessage(content=json.dumps(ambiguous_intents, indent=2))
            clarification_response = await llm_with_tools.ainvoke([clarification_prompt, human_message])
    
            return {
                "messages": [clarification_response]
            }
        tool_calls = [
            ToolCall(
                id=f"call_{int(random.random() * 1e18)}",  # large 18-digit integer
                name=intent["tool"],
                args=intent["arguments"]
            )
            for intent in intents
        ]

        tool_messages = AIMessage(
            content="",
            tool_calls=tool_calls
        )

    
        return {"messages": tool_messages}


    builder = StateGraph(MessagesState)

    builder.add_node('Query_Validation', intent_and_slot_validator)
    builder.add_node('Agent', agent_call)
    builder.add_node('tools', ToolNode(tools))
    # LOGIC
    builder.add_edge(START, 'Query_Validation')
    builder.add_edge('Query_Validation', 'Agent')
    builder.add_conditional_edges('Agent', tools_condition)
    builder.add_edge('tools', 'Agent')

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)

    return graph, tools, sys_prompt, query_validation_prompt