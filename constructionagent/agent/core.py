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
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, ToolCall 
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path
from constructionagent.agent.mcp_layer import MCPLayer
from constructionagent.agent.state import MessagesState
from constructionagent.agent.logger import logger, AgentError, ToolExecutionError, PromptError, ValidationError, ConfigurationError
import json
import random
from constructionagent.agent.mcp_config import REQUIRED_PROMPT_NAMES

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_GENAI_MODEL = os.getenv("GOOGLE_GENAI_MODEL", "gemini-pro")

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
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        try:
            logger.info("Initializing AgentGraph")
            self.mcp_client = MCPLayer()
            self.llm = ChatGoogleGenerativeAI(model=GOOGLE_GENAI_MODEL, temperature=0, google_api_key=GOOGLE_API_KEY)
            self.tools = None
            self.prompts = None
            self.graph = None
            logger.info("AgentGraph initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize AgentGraph", exc_info=True)
            raise ConfigurationError(
                message="Failed to initialize agent",
                error_code="INIT_ERROR",
                details={"error": str(e)}
            )

    async def fetch_tools_and_prompts(self):
        """
        Fetch available tools and required prompts from the MCP layer.
        
        Raises:
            PromptError: If prompt fetching fails
            ToolExecutionError: If tool fetching fails
        """
        try:
            logger.info("Fetching tools and prompts from MCP")
            self.tools = await self.mcp_client.fetch_tools()
            self.llm_with_tools = self.llm.bind_tools(self.tools)
            self.prompts = await self.mcp_client.fetch_prompts(
                list(REQUIRED_PROMPT_NAMES.keys())
            )
            logger.info(f"Successfully fetched {len(self.tools)} tools and {len(self.prompts)} prompts")
        except Exception as e:
            logger.error("Failed to fetch tools and prompts", exc_info=True)
            raise PromptError(
                message="Failed to fetch tools and prompts",
                error_code="FETCH_ERROR",
                details={"error": str(e)}
            )

    async def get_tool_descriptions(self) -> str:
        """
        Generate formatted descriptions of tools fetched from MCP.
        
        Returns:
            str: A numbered list of tool descriptions
            
        Raises:
            ToolExecutionError: If tool descriptions cannot be generated
        """
        try:
            descriptions = []
            for tool in self.tools:
                tool_name = tool.name
                description = tool.description.strip().split("\n")[0]
                args = tool.args_schema.get('properties', {})
                required_args = tool.args_schema.get('required', [])
                arg_list = [
                    f"{arg}: {args.get(arg, {}).get('type', 'string')}"
                    for arg in required_args
                ]
                arg_string = ", ".join(arg_list)
                full_description = f"{tool_name}({arg_string}) → {description}"
                descriptions.append(full_description)
            return "\n".join(f"{i+1}.{d}" for i, d in enumerate(descriptions))
        except Exception as e:
            logger.error("Failed to generate tool descriptions", exc_info=True)
            raise ToolExecutionError(
                message="Failed to generate tool descriptions",
                error_code="TOOL_DESC_ERROR",
                details={"error": str(e)}
            )

    async def intent_and_slot_validator(self, state: MessagesState) -> Dict[str, List[Any]]:
        """
        Validate user query and extract intents and slots.
        
        Args:
            state (MessagesState): Current conversation state
            
        Returns:
            Dict[str, List[Any]]: Updated state with validation results
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            user_query = state['messages'][-1]
            tool_descriptions = await self.get_tool_descriptions()
            validation_sys_message = SystemMessage(
                content=self.prompts['query_validation_prompt'][0].content.format(
                    tool_descriptions=tool_descriptions
                )
            )
            logger.debug("Validating user query", extra={"query": user_query.content})
            result = await self.llm_with_tools.ainvoke([validation_sys_message] + state['messages'])
            return {'messages': [result]}
        except Exception as e:
            logger.error("Query validation failed", exc_info=True)
            raise ValidationError(
                message="Failed to validate query",
                error_code="VALIDATION_ERROR",
                details={"error": str(e)}
            )

    async def agent_call(self, state: MessagesState) -> Dict[str, List[Any]]:
        """
        Process validated intents and execute appropriate tools.
        
        Args:
            state (MessagesState): Current conversation state
            
        Returns:
            Dict[str, List[Any]]: Updated state with tool execution results
            
        Raises:
            ToolExecutionError: If tool execution fails
        """
        try:
            query = state['messages'][-1]
            if isinstance(query, ToolMessage):
                logger.debug("Processing tool message", extra={"Query": query})
                result = await self.llm_with_tools.ainvoke(state['messages'])
                return {'messages': [result]}

            try:
                query = query.content.strip('```json\n').strip('```')
                query = json.loads(query)
            except json.JSONDecodeError as e:
                logger.error("Failed to decode JSON query", exc_info=True)
                return {
                    'messages': [
                        AIMessage(content="Invalid query format. Please try again.")
                    ]
                }

            if query.get("unrelated", 'true'):
                logger.info("Received unrelated query")
                return {
                    "messages": [
                        AIMessage(content="Sorry, the query seems unfamiliar. I am a construction assistant and I can only help with construction related tasks.")
                    ]
                }

            intents = query.get("intents", [])
            ambiguous_intents = [intent for intent in intents if intent["is_ambiguous"]]
            
            if ambiguous_intents:
                logger.info("Handling ambiguous intents", extra={"intents": ambiguous_intents})
                clarification_prompt = SystemMessage(
                    content=self.prompts['clarification_prompt'][0].content
                )
                human_message = HumanMessage(content=json.dumps(ambiguous_intents, indent=2))
                clarification_response = await self.llm_with_tools.ainvoke(
                    [clarification_prompt, human_message]
                )
                return {"messages": [clarification_response]}
            
            # Execute tools for clear intents
            logger.info("Executing tools for clear intents", extra={"intents": intents})
            tool_calls = [
                ToolCall(
                    id=f"call_{int(random.random() * 1e18)}",
                    name=intent["tool"],
                    args=intent["arguments"]
                )
                for intent in intents
            ]
            return {'messages': [AIMessage(content="", tool_calls=tool_calls)]}
            
        except Exception as e:
            logger.error("Tool execution failed", exc_info=True)
            raise ToolExecutionError(
                message="Failed to execute tools",
                error_code="TOOL_EXEC_ERROR",
                details={"error": str(e)}
            )

    async def build_graph(self):
        """
        Construct the agent's processing graph.
        
        Raises:
            ConfigurationError: If graph construction fails
        """
        try:
            logger.info("Building agent graph")
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
            
            # Set up state persistence (in Memory for now)
            memory = MemorySaver()
            self.graph = builder.compile(checkpointer=memory)
            logger.info("Agent graph built successfully")
        except Exception as e:
            logger.error("Failed to build agent graph", exc_info=True)
            raise ConfigurationError(
                message="Failed to build agent graph",
                error_code="GRAPH_BUILD_ERROR",
                details={"error": str(e)}
            )