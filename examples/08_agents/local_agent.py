"""
Local Agent Example — Interactive AI Assistant with Real Tools
Demonstrates GLM-5's function calling, deep thinking, and streaming
in a multi-turn terminal REPL with real local tools.

Tools: read_file, write_file, list_directory, run_command, calculate, get_datetime
"""

import sys
import json
import math
import ast
import operator
import subprocess
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from config import Models, Defaults
from utils.client import get_client, print_error

console = Console()


# =============================================================================
# Safe Expression Evaluator (from multi_function_agent.py)
# =============================================================================

SAFE_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.UAdd: operator.pos, ast.Mod: operator.mod,
}

SAFE_FUNCTIONS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10,
    "exp": math.exp, "pow": pow, "abs": abs,
    "floor": math.floor, "ceil": math.ceil, "round": round,
}

SAFE_CONSTANTS = {"pi": math.pi, "e": math.e}


def safe_eval_node(node):
    """Recursively evaluate an AST node safely."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.Name):
        if node.id in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return SAFE_OPERATORS[op_type](safe_eval_node(node.left), safe_eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return SAFE_OPERATORS[op_type](safe_eval_node(node.operand))
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
            args = [safe_eval_node(arg) for arg in node.args]
            return SAFE_FUNCTIONS[node.func.id](*args)
        raise ValueError(f"Unsupported function: {getattr(node.func, 'id', type(node.func).__name__)}")
    elif isinstance(node, ast.Expression):
        return safe_eval_node(node.body)
    else:
        raise ValueError(f"Unsupported expression type: {type(node).__name__}")


# =============================================================================
# Tool Implementations (real, local)
# =============================================================================

MAX_FILE_SIZE = 100 * 1024  # 100KB
MAX_OUTPUT_SIZE = 10 * 1024  # 10KB
COMMAND_TIMEOUT = 30  # seconds


def read_file(path: str) -> dict:
    """Read a file from the local filesystem."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"error": f"File not found: {p}"}
        if not p.is_file():
            return {"error": f"Not a file: {p}"}
        if p.stat().st_size > MAX_FILE_SIZE:
            return {"error": f"File too large ({p.stat().st_size} bytes, max {MAX_FILE_SIZE})"}
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return {"error": f"Binary file, cannot read as text: {p}"}
        return {"path": str(p), "content": content, "size": len(content)}
    except Exception as e:
        return {"error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Write content to a file on the local filesystem."""
    try:
        p = Path(path).expanduser().resolve()
        existed = p.exists()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"path": str(p), "status": "overwritten" if existed else "created", "size": len(content)}
    except Exception as e:
        return {"error": str(e)}


def list_directory(path: str = ".") -> dict:
    """List contents of a directory with file sizes."""
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            return {"error": f"Directory not found: {p}"}
        if not p.is_dir():
            return {"error": f"Not a directory: {p}"}

        entries = []
        for item in sorted(p.iterdir()):
            entry = {"name": item.name, "type": "dir" if item.is_dir() else "file"}
            if item.is_file():
                entry["size"] = item.stat().st_size
            entries.append(entry)

        return {"path": str(p), "count": len(entries), "entries": entries}
    except Exception as e:
        return {"error": str(e)}


def run_command(command: str) -> dict:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=COMMAND_TIMEOUT, cwd=os.getcwd(),
        )
        stdout = result.stdout[:MAX_OUTPUT_SIZE] if result.stdout else ""
        stderr = result.stderr[:MAX_OUTPUT_SIZE] if result.stderr else ""
        truncated = len(result.stdout or "") > MAX_OUTPUT_SIZE or len(result.stderr or "") > MAX_OUTPUT_SIZE
        resp = {"command": command, "returncode": result.returncode, "stdout": stdout}
        if stderr:
            resp["stderr"] = stderr
        if truncated:
            resp["truncated"] = True
        return resp
    except subprocess.TimeoutExpired:
        return {"error": f"Command timed out after {COMMAND_TIMEOUT}s", "command": command}
    except Exception as e:
        return {"error": str(e), "command": command}


def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression safely using AST parsing."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = safe_eval_node(tree)
        return {"expression": expression, "result": result}
    except SyntaxError as e:
        return {"error": f"Invalid syntax: {e}"}
    except ZeroDivisionError:
        return {"error": "Division by zero"}
    except Exception as e:
        return {"error": str(e)}


def get_datetime() -> dict:
    """Get current date, time, and related info."""
    now = datetime.now()
    return {
        "datetime": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "week_number": now.isocalendar()[1],
        "timezone": str(now.astimezone().tzinfo),
    }


# =============================================================================
# Tool Definitions (JSON schemas for API)
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the local filesystem. Returns file content as text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates parent directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write to"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and subdirectories in a directory with sizes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path (default: current directory)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command and return stdout/stderr. 30s timeout, 10KB output limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"}
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression. Supports +, -, *, /, **, % and functions: sin, cos, tan, sqrt, log, exp, abs, floor, ceil, round. Constants: pi, e.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression, e.g. 'sqrt(16) + 5 * 2'"}
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_datetime",
            "description": "Get current date, time, day of week, and week number.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

FUNCTION_MAP = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "run_command": run_command,
    "calculate": calculate,
    "get_datetime": get_datetime,
}

SYSTEM_PROMPT = (
    "You are a local AI assistant with access to the user's file system and shell.\n"
    "You can read/write files, list directories, run commands, do calculations, and check the time.\n"
    "Think step by step for complex tasks. Use tools when needed — don't guess file contents or command output.\n"
    "Be concise. When showing file contents, summarize unless the user asks for the full output."
)


# =============================================================================
# Streaming Agent Loop
# =============================================================================

def stream_agent_turn(client, messages, show_thinking: bool = True) -> str | None:
    """
    Send messages to GLM-5 with streaming, process response in real-time.
    Returns the final content, or None if only tool calls were made.
    Appends assistant and tool messages to the messages list in-place.
    """
    response = client.create_chat(
        messages=messages,
        tools=TOOLS,
        stream=True,
        tool_stream=True,
        thinking={"type": "enabled"},
        temperature=Defaults.TEMPERATURE,
    )

    reasoning = ""
    content = ""
    tool_calls = {}  # {index: {id, function: {name, arguments}}}
    reasoning_started = False
    content_started = False

    for chunk in response:
        if not chunk.choices or not chunk.choices[0].delta:
            continue

        delta = chunk.choices[0].delta

        # Stream reasoning content
        if hasattr(delta, "reasoning_content") and delta.reasoning_content:
            reasoning += delta.reasoning_content
            if show_thinking:
                if not reasoning_started:
                    console.print("[dim italic]Thinking...[/dim italic]", end="")
                    reasoning_started = True
                print(delta.reasoning_content, end="", flush=True)

        # Stream regular content
        if hasattr(delta, "content") and delta.content:
            if not content_started:
                if reasoning_started and show_thinking:
                    print("\n")  # newline after reasoning
                content_started = True
            content += delta.content
            print(delta.content, end="", flush=True)

        # Accumulate tool calls (concatenate arguments by index)
        if hasattr(delta, "tool_calls") and delta.tool_calls:
            for tc in delta.tool_calls:
                idx = tc.index
                if idx not in tool_calls:
                    tool_calls[idx] = {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name or "",
                            "arguments": tc.function.arguments or "",
                        },
                    }
                else:
                    if tc.function.arguments:
                        tool_calls[idx]["function"]["arguments"] += tc.function.arguments

    # End streaming output
    if reasoning_started and show_thinking and not content_started and not tool_calls:
        print()  # newline after reasoning if no content followed
    if content_started:
        print()  # newline after content

    # Build assistant message for conversation history
    assistant_msg = {"role": "assistant"}
    if content:
        assistant_msg["content"] = content
    if reasoning:
        assistant_msg["reasoning_content"] = reasoning
    if tool_calls:
        assistant_msg["tool_calls"] = [
            {
                "id": tc["id"],
                "type": "function",
                "function": tc["function"],
            }
            for tc in tool_calls.values()
        ]
        if "content" not in assistant_msg:
            assistant_msg["content"] = None

    messages.append(assistant_msg)

    # Execute tool calls if any
    if tool_calls:
        for idx in sorted(tool_calls.keys()):
            tc = tool_calls[idx]
            func_name = tc["function"]["name"]
            raw_args = tc["function"]["arguments"]

            console.print(f"\n[cyan]> {func_name}[/cyan]", end="")

            try:
                func_args = json.loads(raw_args) if raw_args.strip() else {}
            except json.JSONDecodeError as e:
                console.print(f"  [red]JSON parse error: {e}[/red]")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps({"error": f"Invalid arguments JSON: {e}"}),
                })
                continue

            # Show concise args
            arg_summary = ", ".join(f"{k}={repr(v)[:60]}" for k, v in func_args.items())
            if arg_summary:
                console.print(f"({arg_summary})", end="")
            console.print()

            # Execute
            if func_name in FUNCTION_MAP:
                result = FUNCTION_MAP[func_name](**func_args)
            else:
                result = {"error": f"Unknown function: {func_name}"}

            result_str = json.dumps(result)

            # Show result preview
            if "error" in result:
                console.print(f"  [red]{result['error']}[/red]")
            else:
                preview = result_str[:200] + "..." if len(result_str) > 200 else result_str
                console.print(f"  [dim]{preview}[/dim]")

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result_str,
            })

        return None  # signal: tool calls were made, need another iteration

    return content  # final answer


def agent_turn(client, messages, show_thinking: bool = True, max_iterations: int = 10):
    """Run the agent loop for one user turn. Loops until a final answer or max iterations."""
    for i in range(max_iterations):
        result = stream_agent_turn(client, messages, show_thinking)
        if result is not None:
            return result  # final answer produced
    console.print("[yellow]Reached max iterations for this turn.[/yellow]")
    return messages[-1].get("content", "")


# =============================================================================
# REPL & CLI
# =============================================================================

def repl(show_thinking: bool = True):
    """Interactive REPL loop."""
    console.print(Panel.fit(
        "[bold cyan]Local Agent[/bold cyan]\n"
        f"Model: {Models.LLM} | Tools: {len(TOOLS)}\n"
        "Type [bold]quit[/bold] to exit, [bold]clear[/bold] to reset history",
        border_style="cyan",
    ))

    try:
        client = get_client()
    except Exception as e:
        print_error(e, "Failed to initialize client")
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            console.print("[dim]Goodbye.[/dim]")
            break
        if user_input.lower() == "clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            console.print("[dim]History cleared.[/dim]")
            continue

        messages.append({"role": "user", "content": user_input})

        console.print()
        try:
            agent_turn(client, messages, show_thinking)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
        except Exception as e:
            print_error(e, "Agent error")


def single_query(query: str, show_thinking: bool = True):
    """Run a single query and exit."""
    try:
        client = get_client()
    except Exception as e:
        print_error(e, "Failed to initialize client")
        return

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    console.print(f"[bold green]Query:[/bold green] {query}\n")
    try:
        agent_turn(client, messages, show_thinking)
    except Exception as e:
        print_error(e, "Agent error")


def demo(show_thinking: bool = True):
    """Run demo queries to showcase the agent."""
    console.print(Panel.fit(
        "[bold cyan]Local Agent — Demo Mode[/bold cyan]\n"
        f"Model: {Models.LLM} | Running 3 showcase queries",
        border_style="cyan",
    ))

    queries = [
        "What files are in the current directory? Summarize the project structure.",
        "Read the config.py file and tell me which models are configured.",
        "What's the current date and time? Calculate how many days until the end of the year.",
    ]

    try:
        client = get_client()
    except Exception as e:
        print_error(e, "Failed to initialize client")
        return

    for i, query in enumerate(queries, 1):
        console.print(f"\n{'=' * 60}")
        console.print(f"[bold]Demo {i}/{len(queries)}:[/bold] {query}\n")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        try:
            agent_turn(client, messages, show_thinking)
        except Exception as e:
            print_error(e, f"Demo {i} failed")

    console.print(f"\n{'=' * 60}")
    console.print("[bold green]Demo complete.[/bold green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Local Agent — Interactive AI assistant with real tools, powered by GLM-5"
    )
    parser.add_argument("-q", "--query", type=str, help="Run a single query and exit")
    parser.add_argument("--no-thinking", action="store_true", help="Hide thinking/reasoning output")
    parser.add_argument("--demo", action="store_true", help="Run demo queries")

    args = parser.parse_args()
    show = not args.no_thinking

    if args.demo:
        demo(show_thinking=show)
    elif args.query:
        single_query(args.query, show_thinking=show)
    else:
        repl(show_thinking=show)
