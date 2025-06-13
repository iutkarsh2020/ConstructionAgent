"""
State management for the construction agent conversation.

This module defines the state structure used throughout the agent's conversation
graph. It uses TypedDict for type safety and includes message history tracking
through LangGraph's message system.
"""

from dataclasses import dataclass
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
@dataclass
class MessagesState(TypedDict):
    """
    Typed dictionary representing the state of a conversation.
    
    This class defines the structure of the conversation state, including:
    - messages: A list of conversation messages, annotated with LangGraph's
                message tracking system
    - summary: A string containing a summary of the conversation
    
    The messages field uses LangGraph's add_messages annotation to enable
    proper message tracking and state management in the conversation graph.
    """
    messages: Annotated[list[str], add_messages]