"""AI layer: intent understanding and tool dispatch.

Nothing in this package touches the database.  The model's entire capability
surface is the tool registry, and every tool is a thin wrapper over a service.
"""

from app.ai.agent import AgentReply, AssistantAgent
from app.ai.memory import ConversationState, ConversationStore, InMemoryConversationStore
from app.ai.tools.definitions import build_registry
from app.ai.tools.registry import ToolContext, ToolRegistry

__all__ = [
    "AgentReply",
    "AssistantAgent",
    "ConversationState",
    "ConversationStore",
    "InMemoryConversationStore",
    "ToolContext",
    "ToolRegistry",
    "build_registry",
]
