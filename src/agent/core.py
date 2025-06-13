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
from agent.mcp_config import MCP_CLIENT_CONFIG

load_dotenv()

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_GENAI_MODEL = os.environ.get('GOOGLE_GENAI_MODEL')

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

class AgentGraph:
    def __init__(self):
        self.client = MultiServerMCPClient(MCP_CLIENT_CONFIG)
        self.llm = ChatGoogleGenerativeAI(model=GOOGLE_GENAI_MODEL, temperature=0, google_api_key=GOOGLE_API_KEY)
        self.tools = None
        self.llm_with_tools = None
        self.sys_prompt = None
        self.query_validation_prompt = None
        self.graph = None

    async def fetch_tools_and_prompts(self):
        self.tools = await self.client.get_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.sys_prompt = await self.client.get_prompt(server_name="prompt_server", prompt_name="system_prompt")
        self.query_validation_prompt = await self.client.get_prompt(server_name="prompt_server", prompt_name="query_validation_prompt")
        self.clarification_prompt = await self.client.get_prompt(server_name="prompt_server", prompt_name="clarification_prompt")

    async def get_tool_descriptions(self):
        descriptions = []
        for tool in self.tools:
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

    async def intent_and_slot_validator(self, state: MessagesState):
        user_query = state['messages'][-1]
        tool_descriptions = await self.get_tool_descriptions()
        validation_sys_message = SystemMessage(
            content=self.query_validation_prompt[0].content.format(tool_descriptions=tool_descriptions)
        )
        result = await self.llm_with_tools.ainvoke([validation_sys_message, user_query])
        return {'messages': [result]}

    async def agent_call(self, state: MessagesState):
        query = state['messages'][-1]
        if isinstance(query, ToolMessage):
            result = await self.llm_with_tools.ainvoke(state['messages'])
            return {'messages': [result]}
        try:
            query = query.content.strip('```json\n').strip('```')
            query = json.loads(query)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        if query.get("unrelated", 'true'):
            return {
                "messages": [
                    AIMessage(content="Sorry, the query seems unfamiliar. I am a construction assistant and I can only help with construction related tasks.")
                ]
            }
        intents = query.get("intents", [])
        ambiguous_intents = [intent for intent in intents if intent["is_ambiguous"]]
        if ambiguous_intents:
            clarification_prompt = SystemMessage(content=self.clarification_prompt.content)
            human_message = HumanMessage(content=json.dumps(ambiguous_intents, indent=2))
            clarification_response = await self.llm_with_tools.ainvoke([clarification_prompt, human_message])
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

    async def build_graph(self):
        await self.fetch_tools_and_prompts()
        builder = StateGraph(MessagesState)
        builder.add_node('Query_Validation', self.intent_and_slot_validator)
        builder.add_node('Agent', self.agent_call)
        builder.add_node('tools', ToolNode(self.tools))
        # LOGIC
        builder.add_edge(START, 'Query_Validation')
        builder.add_edge('Query_Validation', 'Agent')
        builder.add_conditional_edges('Agent', tools_condition)
        builder.add_edge('tools', 'Agent')
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)
        return self.graph, self.tools, self.sys_prompt, self.query_validation_prompt