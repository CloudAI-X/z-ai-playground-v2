"""
Thinking Mode Example
Demonstrates GLM-4.7's advanced reasoning capabilities:
- Interleaved thinking (reasoning between tool calls)
- Preserved thinking (maintaining reasoning across turns)
- Turn-level thinking (enable/disable per turn)
"""

import sys
import json
import ast
import operator
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.markdown import Markdown

from config import Models
from utils.client import get_client, print_error

console = Console()


# Safe expression evaluator using AST
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


def safe_calculate(expression: str):
    """Safely evaluate a mathematical expression using AST parsing."""
    try:
        tree = ast.parse(expression, mode='eval')
        return safe_eval_node(tree)
    except (SyntaxError, ValueError, ZeroDivisionError) as e:
        raise ValueError(f"Invalid expression: {e}")


def demo_basic_thinking():
    """Demonstrate basic thinking mode with reasoning output."""
    console.print(Panel.fit(
        "[bold cyan]Basic Thinking Mode[/bold cyan]\n"
        "GLM-4.7 shows its reasoning process before answering.",
        border_style="cyan"
    ))

    client = get_client()

    prompt = """Solve this step by step:
    A train leaves Station A at 9:00 AM traveling at 60 mph.
    Another train leaves Station B at 10:00 AM traveling at 80 mph toward Station A.
    If the stations are 280 miles apart, at what time will the trains meet?"""

    console.print(f"\n[bold]Problem:[/bold]\n{prompt}\n")
    console.print("[dim]Processing with thinking enabled...[/dim]\n")

    response = client.create_chat(
        messages=[{"role": "user", "content": prompt}],
        model=Models.LLM,
        stream=True,
        thinking={"type": "enabled"}
    )

    reasoning = ""
    content = ""

    console.print("[bold blue]Reasoning Process:[/bold blue]")
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta:
            delta = chunk.choices[0].delta

            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                reasoning += delta.reasoning_content
                console.print(f"[dim italic]{escape(delta.reasoning_content)}[/dim italic]", end="")

            if hasattr(delta, "content") and delta.content:
                content += delta.content

    console.print("\n")
    console.print(Panel(Markdown(content), title="Final Answer", border_style="green"))

    return {"reasoning": reasoning, "content": content}


def demo_interleaved_thinking():
    """Demonstrate interleaved thinking with function calling."""
    console.print(Panel.fit(
        "[bold cyan]Interleaved Thinking + Function Calling[/bold cyan]\n"
        "Model reasons between tool calls, making step-by-step decisions.",
        border_style="cyan"
    ))

    client = get_client()

    # Define a simple calculator tool
    tools = [{
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate (e.g., '2 + 3 * 4')"
                    }
                },
                "required": ["expression"]
            }
        }
    }]

    prompt = "I need to calculate the total cost: 5 items at $12.99 each, with 8% tax."

    console.print(f"\n[bold]Request:[/bold] {prompt}\n")

    messages = [{"role": "user", "content": prompt}]
    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1

        response = client.create_chat(
            messages=messages,
            model=Models.LLM,
            stream=True,
            tools=tools,
            thinking={"type": "enabled", "clear_thinking": False}
        )

        reasoning = ""
        content = ""
        tool_calls = []

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning += delta.reasoning_content

                if hasattr(delta, "content") and delta.content:
                    content += delta.content

                if hasattr(delta, "tool_calls") and delta.tool_calls:
                    for tc in delta.tool_calls:
                        if tc.index >= len(tool_calls):
                            tool_calls.append({
                                "id": tc.id,
                                "function": {"name": "", "arguments": ""}
                            })
                        if tc.function.name:
                            tool_calls[tc.index]["function"]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments

        if reasoning:
            console.print(Panel(
                reasoning[:500] + "..." if len(reasoning) > 500 else reasoning,
                title=f"Model Reasoning (Step {iteration})",
                border_style="blue"
            ))

        if not tool_calls:
            # No more tool calls, we have the final response
            if content:
                console.print(Panel(Markdown(content), title="Final Response", border_style="green"))
            break

        console.print(Panel(
            json.dumps(tool_calls, indent=2),
            title=f"Tool Calls (Step {iteration})",
            border_style="yellow"
        ))

        # Build assistant message with tool calls
        assistant_msg = {"role": "assistant", "content": content or None, "tool_calls": []}
        tool_results = []

        for tc in tool_calls:
            assistant_msg["tool_calls"].append({
                "id": tc["id"],
                "type": "function",
                "function": tc["function"]
            })

            # Execute tool and collect result
            if tc["function"]["name"] == "calculate":
                try:
                    args = json.loads(tc["function"]["arguments"])
                    expr = args.get("expression", "")
                    result = safe_calculate(expr)
                    console.print(f"[green]Calculated: {expr} = {result}[/green]")
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": str(result)
                    })
                except (json.JSONDecodeError, ValueError) as e:
                    console.print(f"[red]Error: {e}[/red]")
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": f"Error: {e}"
                    })

        messages.append(assistant_msg)
        messages.extend(tool_results)


def demo_turn_level_thinking():
    """Demonstrate enabling/disabling thinking per turn."""
    console.print(Panel.fit(
        "[bold cyan]Turn-Level Thinking Control[/bold cyan]\n"
        "Different turns can have thinking enabled or disabled.",
        border_style="cyan"
    ))

    client = get_client()
    messages = []

    turns = [
        {"message": "What is 2+2?", "thinking": False, "description": "Simple - no thinking needed"},
        {"message": "Explain why water is essential for life", "thinking": True, "description": "Complex - thinking enabled"},
        {"message": "What color is the sky?", "thinking": False, "description": "Simple - no thinking needed"},
    ]

    for i, turn in enumerate(turns, 1):
        console.print(f"\n[bold]Turn {i}[/bold]: {turn['description']}")
        console.print(f"[dim]Thinking: {'Enabled' if turn['thinking'] else 'Disabled'}[/dim]")
        console.print(f"[green]User:[/green] {turn['message']}")

        messages.append({"role": "user", "content": turn["message"]})

        # Use streaming to show progress
        response = client.create_chat(
            messages=messages,
            model=Models.LLM,
            stream=True,
            thinking={"type": "enabled" if turn["thinking"] else "disabled"}
        )

        reply = ""
        reasoning = ""

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning += delta.reasoning_content
                    if turn["thinking"]:
                        console.print(f"[dim italic]{escape(delta.reasoning_content)}[/dim italic]", end="")

                if hasattr(delta, "content") and delta.content:
                    reply += delta.content

        if turn["thinking"] and reasoning:
            console.print()  # New line after reasoning

        messages.append({"role": "assistant", "content": reply})

        console.print(Panel(Markdown(reply), title="AI", border_style="cyan"))


def run():
    """Run all thinking mode demonstrations."""
    console.print(Panel.fit(
        "[bold magenta]GLM-4.7 Thinking Mode Demonstrations[/bold magenta]\n"
        "Exploring deep reasoning capabilities",
        border_style="magenta"
    ))

    try:
        # Demo 1: Basic thinking
        console.print("\n" + "=" * 60 + "\n")
        demo_basic_thinking()

        # Demo 2: Interleaved thinking with tools
        console.print("\n" + "=" * 60 + "\n")
        demo_interleaved_thinking()

        # Demo 3: Turn-level control
        console.print("\n" + "=" * 60 + "\n")
        demo_turn_level_thinking()

        console.print("\n[bold green]All demos completed![/bold green]")

    except Exception as e:
        print_error(e, "Demo failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Thinking Mode Examples")
    parser.add_argument("--basic", action="store_true", help="Run basic thinking demo only")
    parser.add_argument("--interleaved", action="store_true", help="Run interleaved thinking demo only")
    parser.add_argument("--turn-level", action="store_true", help="Run turn-level demo only")

    args = parser.parse_args()

    if args.basic:
        demo_basic_thinking()
    elif args.interleaved:
        demo_interleaved_thinking()
    elif args.turn_level:
        demo_turn_level_thinking()
    else:
        run()
