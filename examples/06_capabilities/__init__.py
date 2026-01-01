"""
Advanced Capabilities Examples
Demonstrates function calling, structured output, context caching, and tool streaming.
"""

from .function_calling import run as run_function_calling
from .structured_output import run as run_structured_output

__all__ = [
    "run_function_calling",
    "run_structured_output",
]
