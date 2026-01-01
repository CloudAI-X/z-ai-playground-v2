"""
Built-in Tools Examples
Demonstrates web search API and web search in chat.
"""

from .web_search_api import run as run_web_search_api
from .web_search_chat import run as run_web_search_chat

__all__ = [
    "run_web_search_api",
    "run_web_search_chat",
]
