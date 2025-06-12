from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class MessagesState(TypedDict):
    messages: Annotated[list[str], add_messages]
    summary: str 