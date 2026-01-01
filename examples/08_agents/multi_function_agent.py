"""
Multi-Function Agent Example
Demonstrates an autonomous agent that combines multiple tools:
- Calculator
- Time/Date
- Web Search
- Weather
"""

import sys
import json
import math
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from config import Models
from utils.client import get_client, print_error

console = Console()


# =============================================================================
# Tool Implementations
# =============================================================================

def calculate(expression: str) -> dict:
    """Evaluate mathematical expressions safely."""
    try:
        # Define allowed functions
        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
            "exp": math.exp, "pow": pow, "abs": abs,
            "pi": math.pi, "e": math.e
        }

        # Evaluate with restricted namespace
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": str(e)}


def get_current_datetime(timezone: str = "local") -> dict:
    """Get current date and time information."""
    now = datetime.now()
    return {
        "timezone": timezone,
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "week_number": now.isocalendar()[1],
        "is_weekend": now.weekday() >= 5
    }


def get_weather(location: str, unit: str = "celsius") -> dict:
    """Simulate weather data for a location."""
    # Simulated weather data
    import random
    random.seed(hash(location) % 100)  # Consistent "random" data per location

    conditions = ["Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Overcast"]
    temp_base = random.randint(10, 30)

    temp = temp_base if unit == "celsius" else round(temp_base * 9/5 + 32)

    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": random.choice(conditions),
        "humidity": random.randint(30, 80),
        "wind_speed": random.randint(5, 25),
        "wind_unit": "km/h"
    }


def search_web(query: str, num_results: int = 3) -> dict:
    """Simulate web search results."""
    # In a real implementation, this would call the actual web search API
    return {
        "query": query,
        "results": [
            {"title": f"Result 1 for '{query}'", "snippet": "This is a simulated search result..."},
            {"title": f"Result 2 for '{query}'", "snippet": "Another simulated result..."},
            {"title": f"Result 3 for '{query}'", "snippet": "Third simulated result..."},
        ][:num_results],
        "note": "This is simulated data. Use web_search_chat.py for real searches."
    }


def convert_units(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert between common units."""
    conversions = {
        # Length
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x * 1.60934,
        ("m", "ft"): lambda x: x * 3.28084,
        ("ft", "m"): lambda x: x / 3.28084,
        # Temperature
        ("celsius", "fahrenheit"): lambda x: x * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        # Weight
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x / 2.20462,
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return {
            "original": {"value": value, "unit": from_unit},
            "converted": {"value": round(result, 2), "unit": to_unit}
        }
    else:
        return {"error": f"Cannot convert from {from_unit} to {to_unit}"}


# =============================================================================
# Tool Definitions for API
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate mathematical expressions. Supports basic operations (+, -, *, /, **) and functions (sin, cos, sqrt, log, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g., 'sqrt(16) + 5 * 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time, including day of week and week number",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (default: local)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather conditions for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return (1-5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_units",
            "description": "Convert between units (length: km/miles, m/ft; temperature: celsius/fahrenheit; weight: kg/lbs)",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Value to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "Original unit"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Target unit"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    }
]

# Function dispatch map
FUNCTION_MAP = {
    "calculate": calculate,
    "get_current_datetime": get_current_datetime,
    "get_weather": get_weather,
    "search_web": search_web,
    "convert_units": convert_units
}


def execute_function(name: str, arguments: dict) -> str:
    """Execute a function and return JSON string result."""
    if name in FUNCTION_MAP:
        result = FUNCTION_MAP[name](**arguments)
        return json.dumps(result)
    return json.dumps({"error": f"Unknown function: {name}"})


# =============================================================================
# Agent Runner
# =============================================================================

def run(query: str = None, max_iterations: int = 5):
    """
    Run the multi-function agent to answer a query.

    Args:
        query: User's question or task
        max_iterations: Maximum number of tool-calling iterations
    """
    console.print(Panel.fit(
        "[bold cyan]Multi-Function Agent[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Autonomous agent with multiple tools",
        border_style="cyan"
    ))

    query = query or "What's the weather in Tokyo, and if it's above 20 celsius, convert that to fahrenheit. Also, what day of the week is it?"

    console.print(f"\n[bold]User Query:[/bold] {query}\n")

    # Show available tools
    table = Table(title="Available Tools")
    table.add_column("Tool", style="cyan")
    table.add_column("Description", style="white")

    for tool in TOOLS:
        func = tool["function"]
        table.add_row(func["name"], func["description"][:60] + "...")

    console.print(table)
    console.print()

    try:
        client = get_client()
        messages = [{"role": "user", "content": query}]

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            console.print(f"[dim]Iteration {iteration}...[/dim]")

            # Get model response
            response = client.create_chat(
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message

            # Check if model wants to call tools
            if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
                console.print(f"\n[bold]Agent calling {len(assistant_message.tool_calls)} tool(s):[/bold]")

                # Add assistant message
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    console.print(f"\n  [cyan]→ {func_name}[/cyan]")
                    console.print(f"    Args: {json.dumps(func_args)}")

                    result = execute_function(func_name, func_args)
                    result_data = json.loads(result)

                    console.print(f"    Result: {json.dumps(result_data, indent=2)}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

            else:
                # Model has finished - return final response
                final_content = assistant_message.content

                console.print("\n")
                console.print(Panel(
                    Markdown(final_content),
                    title="Agent Response",
                    border_style="green"
                ))

                return {
                    "query": query,
                    "iterations": iteration,
                    "response": final_content
                }

        console.print("[yellow]Max iterations reached[/yellow]")
        return None

    except Exception as e:
        print_error(e, "Agent execution failed")
        return None


def demo_complex_queries():
    """Demo: Handle various complex queries."""
    console.print(Panel.fit(
        "[bold cyan]Complex Query Demo[/bold cyan]\n"
        "Testing agent with various tasks",
        border_style="cyan"
    ))

    queries = [
        "Calculate the area of a circle with radius 5, and tell me what time it is",
        "I'm planning a trip to Paris. What's the weather there? And how far is it from London in miles if it's 450km?",
        "What's 25% of 840, and is today a weekday or weekend?",
    ]

    results = []
    for query in queries:
        console.print(f"\n{'='*60}")
        result = run(query)
        if result:
            results.append(result)

    # Summary
    console.print("\n")
    table = Table(title="Execution Summary")
    table.add_column("Query", style="white", width=50)
    table.add_column("Iterations", style="cyan")

    for result in results:
        table.add_row(
            result["query"][:50] + "...",
            str(result["iterations"])
        )

    console.print(table)

    return results


def demo_step_by_step():
    """Demo: Show detailed step-by-step agent reasoning."""
    console.print(Panel.fit(
        "[bold cyan]Step-by-Step Agent Demo[/bold cyan]\n"
        "Detailed view of agent decision-making",
        border_style="cyan"
    ))

    query = """
    Help me plan my day. I need to know:
    1. What day and time it is
    2. The weather in my city (New York)
    3. If the temperature is above 60°F, convert it to Celsius
    4. Calculate how many hours until 6 PM if it's before that
    """

    console.print(f"[bold]Task:[/bold]\n{query}\n")
    console.print("[dim]Watch the agent reason through this multi-step task...[/dim]\n")

    return run(query, max_iterations=10)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Function Agent")
    parser.add_argument("-q", "--query", type=str, help="Query for the agent")
    parser.add_argument("--demo-complex", action="store_true",
                        help="Run complex queries demo")
    parser.add_argument("--demo-step", action="store_true",
                        help="Run step-by-step demo")

    args = parser.parse_args()

    if args.demo_complex:
        demo_complex_queries()
    elif args.demo_step:
        demo_step_by_step()
    else:
        run(query=args.query)
