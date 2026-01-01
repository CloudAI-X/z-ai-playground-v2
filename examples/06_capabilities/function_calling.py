"""
Function Calling Example
Demonstrates GLM-4.7's ability to call functions and use tools.
"""

import sys
import json
import re
import ast
import operator
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from config import Models, Defaults
from utils.client import get_client, print_error

console = Console()


# Lazy client for web search
_search_client = None


def _get_search_client():
    """Get cached search client."""
    global _search_client
    if _search_client is None:
        _search_client = get_client()
    return _search_client


# Define available tools
def get_current_weather(location: str, unit: str = "celsius") -> dict:
    """Get real weather for a location using web search."""
    try:
        client = _get_search_client()

        # Search for current weather
        response = client.client.web_search.web_search(
            search_engine="search-prime",
            search_query=f"current weather in {location} temperature",
            count=3,
            search_recency_filter="day"  # Get recent results
        )

        if hasattr(response, "search_result") and response.search_result:
            # Extract weather info from search results
            results = response.search_result
            weather_info = ""
            for result in results:
                content = getattr(result, "content", "")
                if content:
                    weather_info += content + " "

            return {
                "location": location,
                "source": "web_search (real-time)",
                "unit": unit,
                "search_results": weather_info[:500] if weather_info else "No weather data found",
                "note": "Real weather data from web search"
            }
        else:
            return {
                "location": location,
                "error": "No search results found",
                "note": "Try a different location or check your connection"
            }

    except Exception as e:
        return {
            "location": location,
            "error": str(e),
            "note": "Web search failed - check API connection"
        }


def get_current_time(timezone: str = "UTC") -> dict:
    """Get the current time."""
    now = datetime.now()
    return {
        "timezone": timezone,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "day_of_week": now.strftime("%A")
    }


def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression safely using AST parsing."""
    # Supported operators for safe evaluation
    SAFE_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
        ast.Mod: operator.mod,
    }

    def safe_eval_node(node):
        """Recursively evaluate an AST node safely."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            left = safe_eval_node(node.left)
            right = safe_eval_node(node.right)
            return SAFE_OPERATORS[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ValueError(f"Unsupported operator: {op_type.__name__}")
            operand = safe_eval_node(node.operand)
            return SAFE_OPERATORS[op_type](operand)
        elif isinstance(node, ast.Expression):
            return safe_eval_node(node.body)
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")

    try:
        # Parse expression into AST
        tree = ast.parse(expression, mode='eval')
        result = safe_eval_node(tree)
        return {"expression": expression, "result": result}
    except SyntaxError as e:
        return {"error": f"Invalid expression syntax: {e}"}
    except ValueError as e:
        return {"error": str(e)}
    except ZeroDivisionError:
        return {"error": "Division by zero"}
    except Exception as e:
        return {"error": f"Calculation failed: {e}"}


# Tool definitions for the API
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get real-time weather for a location using web search",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name, e.g., 'Beijing', 'New York'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit preference"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (default: UTC)"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g., '(2 + 3) * 4'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Function dispatch
FUNCTION_MAP = {
    "get_current_weather": get_current_weather,
    "get_current_time": get_current_time,
    "calculate": calculate,
}


def execute_function(name: str, arguments: dict) -> str:
    """Execute a function and return the result as a string."""
    if name in FUNCTION_MAP:
        result = FUNCTION_MAP[name](**arguments)
        return json.dumps(result)
    return json.dumps({"error": f"Unknown function: {name}"})


def run(user_query: str = None):
    """
    Demonstrate function calling with GLM-4.7.

    Args:
        user_query: User's question that may require tool use
    """
    console.print(Panel.fit(
        "[bold cyan]Function Calling Example[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Autonomous tool selection and execution",
        border_style="cyan"
    ))

    user_query = user_query or "What's the weather in Beijing and what time is it?"

    console.print(f"\n[bold]User Query:[/bold] {user_query}\n")

    # Show available tools
    table = Table(title="Available Tools")
    table.add_column("Function", style="cyan")
    table.add_column("Description", style="white")

    for tool in TOOLS:
        func = tool["function"]
        table.add_row(func["name"], func["description"])

    console.print(table)
    console.print()

    try:
        client = get_client()
        messages = [{"role": "user", "content": user_query}]

        console.print("[dim]Sending request with tools...[/dim]\n")

        # First call - model decides which tools to use
        response = client.create_chat(
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=Defaults.TEMPERATURE  # GLM-4.7 best practice
        )

        assistant_message = response.choices[0].message

        # Check if the model wants to call functions
        if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
            console.print("[bold]Model requested function calls:[/bold]\n")

            # Add assistant message to conversation
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

            # Execute each function call
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name

                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError as e:
                    console.print(f"  [red]→ {func_name}[/red]")
                    console.print(f"    [red]JSON parse error: {e}[/red]")
                    result = json.dumps({"error": f"Invalid JSON arguments: {e}"})
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                    continue

                console.print(f"  [cyan]→ {func_name}[/cyan]")
                console.print(f"    Arguments: {func_args}")

                # Execute the function
                result = execute_function(func_name, func_args)

                console.print(f"    Result: {result}\n")

                # Add tool response to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Second call - model generates final response
            console.print("[dim]Generating final response...[/dim]\n")

            final_response = client.create_chat(
                messages=messages,
                tools=TOOLS,
                temperature=Defaults.TEMPERATURE
            )

            final_content = final_response.choices[0].message.content

            console.print(Panel(
                final_content,
                title="Final Response",
                border_style="green"
            ))

            return {
                "query": user_query,
                "tool_calls": [tc.function.name for tc in assistant_message.tool_calls],
                "response": final_content
            }

        else:
            # Model responded directly without calling functions
            content = assistant_message.content
            console.print(Panel(
                content,
                title="Direct Response (no tools needed)",
                border_style="yellow"
            ))

            return {
                "query": user_query,
                "tool_calls": [],
                "response": content
            }

    except Exception as e:
        print_error(e, "Function calling failed")
        return None


def demo_multi_step_reasoning():
    """Demo: Complex query requiring multiple function calls."""
    console.print(Panel.fit(
        "[bold cyan]Multi-Step Reasoning Demo[/bold cyan]\n"
        "Complex queries requiring multiple tools",
        border_style="cyan"
    ))

    queries = [
        "What's 15% of 847.50, and what's the weather in Tokyo?",
        "If it's 22 degrees celsius in Beijing, what's that in fahrenheit? Calculate it.",
        "What time is it and what's (24 * 60) minutes in a day?",
    ]

    results = []
    for query in queries:
        console.print(f"\n[bold]Query:[/bold] {query}")
        console.rule()
        result = run(query)
        if result:
            results.append(result)

    return results


def demo_forced_tool_use():
    """Demo: Force the model to use a specific tool."""
    console.print(Panel.fit(
        "[bold cyan]Forced Tool Use Demo[/bold cyan]\n"
        "Requiring specific function calls",
        border_style="cyan"
    ))

    try:
        client = get_client()

        # Force the model to use a specific function
        messages = [{"role": "user", "content": "Hello, how are you?"}]

        console.print("[bold]Query:[/bold] Hello, how are you?")
        console.print("[dim]Forcing use of get_current_time...[/dim]\n")

        response = client.create_chat(
            messages=messages,
            tools=TOOLS,
            tool_choice={"type": "function", "function": {"name": "get_current_time"}}
        )

        assistant_message = response.choices[0].message

        if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
            for tc in assistant_message.tool_calls:
                console.print(f"[green]Forced function call:[/green] {tc.function.name}")
                console.print(f"Arguments: {tc.function.arguments}")
        else:
            console.print("[yellow]No tool call made[/yellow]")

    except Exception as e:
        print_error(e, "Forced tool use failed")


def show_tool_definitions():
    """Display the JSON tool definitions."""
    console.print(Panel.fit(
        "[bold cyan]Tool Definitions[/bold cyan]\n"
        "JSON schema for function definitions",
        border_style="cyan"
    ))

    tool_json = json.dumps(TOOLS, indent=2)
    syntax = Syntax(tool_json, "json", theme="monokai", line_numbers=True)
    console.print(syntax)


def demo_streaming_tool_calls():
    """
    Demo: Streaming function calling with tool_stream=True.

    This demonstrates the GLM-4.7 best practice of streaming tool call
    parameters and concatenating arguments across chunks.
    """
    console.print(Panel.fit(
        "[bold cyan]Streaming Tool Calls Demo[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "GLM-4.7 tool_stream=True for real-time tool parameters",
        border_style="cyan"
    ))

    user_query = "What's the weather in Beijing and calculate 15% of 847.50"
    console.print(f"\n[bold]Query:[/bold] {user_query}\n")

    try:
        client = get_client()
        messages = [{"role": "user", "content": user_query}]

        console.print("[dim]Streaming with tool_stream=True...[/dim]\n")

        # Use streaming with tool_stream=True (GLM-4.7 feature)
        response = client.create_chat(
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=True,
            tool_stream=True,  # GLM-4.7: Enable streaming tool parameters
            temperature=Defaults.TEMPERATURE
        )

        # Concatenate tool arguments across chunks (best practice pattern from docs)
        final_tool_calls = {}
        content = ""

        # Track detected tools for clean output
        detected_tools = []

        for chunk in response:
            if not chunk.choices or not chunk.choices[0].delta:
                continue

            delta = chunk.choices[0].delta

            # Handle content
            if hasattr(delta, "content") and delta.content:
                content += delta.content

            # Handle streaming tool calls with argument concatenation
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tool_call in delta.tool_calls:
                    idx = tool_call.index

                    if idx not in final_tool_calls:
                        # Initialize new tool call entry
                        final_tool_calls[idx] = {
                            "id": tool_call.id,
                            "function": {
                                "name": tool_call.function.name or "",
                                "arguments": tool_call.function.arguments or ""
                            }
                        }
                        if tool_call.function.name:
                            detected_tools.append(tool_call.function.name)
                    else:
                        # Concatenate arguments (key pattern from GLM-4.7 docs)
                        if tool_call.function.arguments:
                            final_tool_calls[idx]["function"]["arguments"] += tool_call.function.arguments

        # Show what tools were detected
        if detected_tools:
            console.print(f"[dim]Tools called: {', '.join(detected_tools)}[/dim]")
            console.print("[dim]Executing...[/dim]")

        console.print("\n")

        # Display and execute tool calls with clean formatting
        if final_tool_calls:
            console.print()

            for idx, tc in sorted(final_tool_calls.items()):
                func_name = tc["function"]["name"]
                func_args_str = tc["function"]["arguments"]

                try:
                    func_args = json.loads(func_args_str)
                    # Execute the function
                    result_str = execute_function(func_name, func_args)
                    result = json.loads(result_str)

                    # Format output nicely based on function type
                    if func_name == "get_current_weather":
                        location = result.get("location", "Unknown")
                        source = result.get("source", "unknown")
                        search_results = result.get("search_results", "")

                        # Try to extract key weather info from search results
                        text = search_results

                        # Extract temperature (look for patterns like "16F", "-1C", "31°")
                        temp_match = re.search(r'(-?\d+)\s*[°]?\s*[CF]', text, re.IGNORECASE)
                        temp = temp_match.group(0) if temp_match else "N/A"

                        # Extract condition (Cloudy, Sunny, Rain, etc.)
                        conditions = ["Cloudy", "Sunny", "Clear", "Rain", "Snow", "Partly cloudy",
                                     "Overcast", "Fog", "Hazy", "Thunderstorm", "Windy"]
                        condition = "N/A"
                        for c in conditions:
                            if c.lower() in text.lower():
                                condition = c
                                break

                        # Extract RealFeel if present
                        realfeel_match = re.search(r'RealFeel\s*[®]?\s*(-?\d+)', text, re.IGNORECASE)
                        realfeel = realfeel_match.group(1) + "°" if realfeel_match else None

                        # Build clean display
                        weather_display = f"[bold yellow]{temp}[/bold yellow]  [cyan]{condition}[/cyan]"
                        if realfeel:
                            weather_display += f"  [dim](Feels like {realfeel})[/dim]"

                        console.print(Panel(
                            f"[bold]{location}[/bold]\n\n"
                            f"{weather_display}\n\n"
                            f"[dim]Source: {source}[/dim]",
                            title=f"[cyan]Weather[/cyan]",
                            border_style="green"
                        ))

                    elif func_name == "calculate":
                        expr = result.get("expression", "")
                        calc_result = result.get("result", "")
                        console.print(Panel(
                            f"[bold]Expression:[/bold] {expr}\n"
                            f"[bold green]Result:[/bold green] [yellow]{calc_result}[/yellow]",
                            title=f"[cyan]Calculation[/cyan]",
                            border_style="green"
                        ))

                    elif func_name == "get_current_time":
                        console.print(Panel(
                            f"[bold]Time:[/bold] {result.get('time', '')}\n"
                            f"[bold]Date:[/bold] {result.get('date', '')}\n"
                            f"[bold]Day:[/bold] {result.get('day_of_week', '')}",
                            title=f"[cyan]Current Time[/cyan]",
                            border_style="green"
                        ))

                    else:
                        # Generic fallback
                        console.print(Panel(
                            json.dumps(result, indent=2, ensure_ascii=False),
                            title=f"[cyan]{func_name}[/cyan]",
                            border_style="green"
                        ))

                except json.JSONDecodeError as e:
                    console.print(Panel(
                        f"[red]JSON parse error: {e}[/red]\n"
                        f"Raw: {func_args_str}",
                        title=f"[red]Error: {func_name}[/red]",
                        border_style="red"
                    ))

        return final_tool_calls

    except Exception as e:
        print_error(e, "Streaming tool calls failed")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Function Calling Example")
    parser.add_argument("-q", "--query", type=str, help="User query to process")
    parser.add_argument("--demo-multi", action="store_true",
                        help="Run multi-step reasoning demo")
    parser.add_argument("--demo-forced", action="store_true",
                        help="Run forced tool use demo")
    parser.add_argument("--demo-streaming", action="store_true",
                        help="Run streaming tool calls demo (tool_stream=True)")
    parser.add_argument("--show-tools", action="store_true",
                        help="Show tool definitions")

    args = parser.parse_args()

    if args.demo_multi:
        demo_multi_step_reasoning()
    elif args.demo_forced:
        demo_forced_tool_use()
    elif args.demo_streaming:
        demo_streaming_tool_calls()
    elif args.show_tools:
        show_tool_definitions()
    else:
        run(user_query=args.query)
