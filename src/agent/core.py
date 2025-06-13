"""
Core module for the Construction Agent system.

This module implements the main agent architecture using LangGraph for orchestrating
conversational AI workflows. It handles tool management, prompt management, and
implements a state-based graph for processing user queries through validation,
intent recognition, and tool execution.

The module uses Google's Generative AI (Gemini) as the underlying LLM and integrates
with a custom MCP (Model Control Panel) layer for tool and prompt management.

Key Components:
    - AgentGraph: Main class that orchestrates the agent's workflow
    - MessagesState: State management for conversation history
    - Tool management and execution
    - Intent validation and processing
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, ToolCall 
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path
from src.agent.mcp_layer import MCPLayer
from src.agent.state import MessagesState
from src.agent.mcp_config import MCP_CLIENT_CONFIG, REQUIRED_PROMPT_NAMES
import json
import random

load_dotenv()
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_GENAI_MODEL = os.environ.get('GOOGLE_GENAI_MODEL')
# Get the project root directory for file operations
PROJECT_ROOT = Path(__file__).parent.parent.parent

class AgentGraph:
    """
    Main agent class that implements the conversational AI workflow using LangGraph.
    
    This class manages the entire lifecycle of user interactions, including:
    - Tool and prompt management through MCP layer
    - Query validation and intent recognition
    - Tool execution and response generation
    - State management for conversation history
    
    """

    def __init__(self):
        """
        Initialize the AgentGraph with required components.
        
        Sets up:
        - MCP client for tool and prompt management
        - Google Generative AI model (Gemini)
        - Tools and prompts (initialized as None, fetched later)
        - Graph structure (initialized as None, built later)
        """
        self.mcp_client = MCPLayer()
        self.llm = ChatGoogleGenerativeAI(model=GOOGLE_GENAI_MODEL, temperature=0, google_api_key=GOOGLE_API_KEY)
        self.tools = None
        self.prompts = None
        self.graph = None

    async def fetch_tools_and_prompts(self):
        """
        Fetch available tools and required prompts from the MCP layer.
        
        This method:
        1. Retrieves available tools from MCP
        2. Binds tools to the LLM for tool-aware responses
        3. Fetches required prompts for various conversation stages
        
        The fetched tools and prompts are stored in instance variables for use
        throughout the conversation.
        """
        self.tools = await self.mcp_client.fetch_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.prompts = await self.mcp_client.fetch_prompts(list(REQUIRED_PROMPT_NAMES.keys()))

    async def get_tool_descriptions(self):
        """
        Generate formatted descriptions of tools fetched from MCP.
        
        Returns:
            str: A numbered list of tool descriptions, including:
                - Tool name
                - Required arguments and their types
                - Tool description
                
        Example output:
            1. tool_name(arg1: string, arg2: number) → Tool description
            2. another_tool(arg: boolean) → Another tool description
        """
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
        """
        Validate user query and extract intents and slots.
        
        Args:
            state (MessagesState): Current conversation state containing message history
            
        Returns:
            dict: Updated state with validation results, including:
                - Whether the query is construction-related
                - Extracted intents and their parameters
                - Ambiguity flags for intents requiring clarification
        """
        user_query = state['messages'][-1]
        tool_descriptions = await self.get_tool_descriptions()
        validation_sys_message = SystemMessage(
            content=self.prompts['query_validation_prompt'][0].content.format(tool_descriptions=tool_descriptions)
        )
        result = await self.llm_with_tools.ainvoke([validation_sys_message] + state['messages'])
        return {'messages': [result]}

    async def agent_call(self, state: MessagesState):
        """
        Process validated intents and execute appropriate tools.
        
        This method handles:
        1. Processing tool responses
        2. Handling ambiguous intents through clarification
        3. Executing tools for clear intents
        4. Generating appropriate responses
        
        Args:
            state (MessagesState): Current conversation state
            
        Returns:
            dict: Updated state with:
                - Tool execution results
                - Clarification requests for ambiguous intents
                - Error messages for unrelated queries
        """
        query = state['messages'][-1]
        if isinstance(query, ToolMessage):
            result = await self.llm_with_tools.ainvoke(state['messages'])
            return {'messages': [result]}
        try:
            query = query.content.strip('```json\n').strip('```')
            query = json.loads(query)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {'messages': [AIMessage(content="Some error occurred. Please try again.")]}
        to_return = {}
        if query.get("unrelated", 'true'):
            to_return = {"messages": [AIMessage(content="Sorry, the query seems unfamiliar. I am a construction assistant and I can only help with construction related tasks.")]}
        else: 
            intents = query.get("intents", [])
            ambiguous_intents = [intent for intent in intents if intent["is_ambiguous"]]
            if ambiguous_intents:
                # Handle ambiguous intents by requesting clarification
                clarification_prompt = SystemMessage(content=self.prompts['clarification_prompt'][0].content)
                human_message = HumanMessage(content=json.dumps(ambiguous_intents, indent=2))
                clarification_response = await self.llm_with_tools.ainvoke([clarification_prompt, human_message])
                to_return = {"messages": [clarification_response]}
            else:
                # Execute tools for clear intents
                tool_calls = [
                    ToolCall(
                        id=f"call_{int(random.random() * 1e18)}",  # Generate unique call ID
                        name=intent["tool"],
                        args=intent["arguments"]
                    )
                    for intent in intents
                ]
                # Tool_calls for clear intents
                to_return = {'messages':[AIMessage(content="", tool_calls=tool_calls)]}
        return to_return

    async def build_graph(self):
        """
        Construct the agent's processing graph.
        
        This method:
        1. Fetches required tools and prompts
        2. Builds a state graph with nodes for:
            - Query validation
            - Agent processing
            - Tool execution
        3. Defines the flow between nodes
        4. Sets up memory for state persistence
        
        The graph implements the following flow:
        START → Query_Validation → Agent → (Tools or END)
        """
        await self.fetch_tools_and_prompts()
        builder = StateGraph(MessagesState)
        builder.add_node('Query_Validation', self.intent_and_slot_validator)
        builder.add_node('Agent', self.agent_call)
        builder.add_node('tools', ToolNode(self.tools))
        
        # Define graph flow
        builder.add_edge(START, 'Query_Validation')
        builder.add_edge('Query_Validation', 'Agent')
        builder.add_conditional_edges('Agent', tools_condition)
        builder.add_edge('tools', 'Agent')
        
        # Set up state persistence(in Memory for now)
        memory = MemorySaver()
        self.graph = builder.compile(checkpointer=memory)