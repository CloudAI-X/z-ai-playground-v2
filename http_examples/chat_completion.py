"""
HTTP Chat Completion Example
Demonstrates direct HTTP API calls for chat completion.
"""

import sys
import json
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from config import API_KEY, BASE_URL, ENDPOINTS, Models, Defaults

console = Console()

# HTTP request timeouts (connect, read) in seconds
HTTP_TIMEOUT = 60  # For non-streaming requests
HTTP_TIMEOUT_STREAMING = (20, 240)  # (connect, read) for streaming requests


def run(prompt: str = None, stream: bool = False):
    """
    Make a direct HTTP API call for chat completion.

    Args:
        prompt: User message
        stream: Whether to stream the response
    """
    console.print(Panel.fit(
        "[bold cyan]HTTP Chat Completion[/bold cyan]\n"
        "Direct API call without SDK",
        border_style="cyan"
    ))

    prompt = prompt or "Explain what an API is in simple terms."

    console.print(f"\n[bold]Prompt:[/bold] {prompt}")
    console.print(f"[bold]Stream:[/bold] {stream}\n")

    # Prepare request
    url = BASE_URL.rstrip("/") + ENDPOINTS["chat"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Models.LLM,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": stream,
        "thinking": {"type": "enabled"},
        "temperature": Defaults.TEMPERATURE,  # GLM-4.7 best practice
        "max_tokens": Defaults.MAX_TOKENS
    }

    # Show the request
    console.print("[bold]Request:[/bold]")
    syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
    console.print(syntax)
    console.print()

    try:
        console.print("[dim]Sending request...[/dim]\n")

        if stream:
            # Streaming request
            response = requests.post(url, headers=headers, json=payload, stream=True, timeout=HTTP_TIMEOUT_STREAMING)
            response.raise_for_status()

            console.print("[bold]Streaming Response:[/bold]")
            full_content = ""
            full_reasoning = ""

            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data:"):
                        data_str = line_str[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    full_content += content
                                    console.print(content, end="")
                                if "reasoning_content" in delta:
                                    full_reasoning += delta["reasoning_content"]
                        except json.JSONDecodeError:
                            pass

            console.print("\n")

            if full_reasoning:
                console.print(Panel(
                    full_reasoning[:300] + "...",
                    title="Reasoning",
                    border_style="blue"
                ))

            return {"content": full_content, "reasoning": full_reasoning}

        else:
            # Non-streaming request
            response = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
            response.raise_for_status()

            result = response.json()

            # Display response
            console.print("[bold]Response:[/bold]")
            syntax = Syntax(json.dumps(result, indent=2, ensure_ascii=False), "json", theme="monokai")
            console.print(syntax)

            # Extract content
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                console.print(Panel(content, title="Content", border_style="green"))

            return result

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e.response.status_code}[/red]")
        console.print(f"[dim]{e.response.text}[/dim]")
        return None
    except requests.exceptions.Timeout as e:
        console.print(f"[red]Timeout Error: Request timed out[/red]")
        console.print(f"[dim]{e}[/dim]")
        return None
    except Exception as e:
        console.print(f"[red]Error ({type(e).__name__}): {e}[/red]")
        return None


def demo_with_thinking():
    """Demo: HTTP request with thinking mode options."""
    console.print(Panel.fit(
        "[bold cyan]Thinking Mode HTTP Demo[/bold cyan]\n"
        "Direct API calls with thinking parameters",
        border_style="cyan"
    ))

    url = BASE_URL.rstrip("/") + ENDPOINTS["chat"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Different thinking configurations
    configs = [
        {"name": "Thinking Enabled", "thinking": {"type": "enabled"}},
        {"name": "Thinking Disabled", "thinking": {"type": "disabled"}},
    ]

    prompt = "What is 15% of 847?"

    for config in configs:
        console.print(f"\n[bold]{config['name']}:[/bold]")

        payload = {
            "model": Models.LLM,
            "messages": [{"role": "user", "content": prompt}],
            "thinking": config["thinking"]
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
            response.raise_for_status()

            result = response.json()

            if "choices" in result:
                message = result["choices"][0]["message"]
                content = message.get("content", "")
                reasoning = message.get("reasoning_content", "")

                console.print(f"  Content: {content[:100]}")
                if reasoning:
                    console.print(f"  Reasoning: {reasoning[:100]}...")

        except Exception as e:
            console.print(f"  [red]Error ({type(e).__name__}): {e}[/red]")


def demo_with_tools():
    """Demo: HTTP request with function calling."""
    console.print(Panel.fit(
        "[bold cyan]Function Calling HTTP Demo[/bold cyan]\n"
        "Direct API calls with tools",
        border_style="cyan"
    ))

    url = BASE_URL.rstrip("/") + ENDPOINTS["chat"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    }]

    payload = {
        "model": Models.LLM,
        "messages": [{"role": "user", "content": "What's the weather in Tokyo?"}],
        "tools": tools,
        "tool_choice": "auto"
    }

    console.print("[bold]Request with tools:[/bold]")
    syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
    console.print(syntax)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        result = response.json()

        console.print("\n[bold]Response:[/bold]")
        syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
        console.print(syntax)

        # Check for tool calls
        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]
            if "tool_calls" in message:
                console.print("\n[green]Tool calls detected![/green]")
                for tc in message["tool_calls"]:
                    console.print(f"  Function: {tc['function']['name']}")
                    console.print(f"  Arguments: {tc['function']['arguments']}")

    except Exception as e:
        console.print(f"[red]Error ({type(e).__name__}): {e}[/red]")


def demo_streaming_tool_calls():
    """Demo: HTTP request with streaming tool calls (tool_stream=True)."""
    console.print(Panel.fit(
        "[bold cyan]Streaming Tool Calls HTTP Demo[/bold cyan]\n"
        "GLM-4.7 tool_stream=True via direct API",
        border_style="cyan"
    ))

    url = BASE_URL.rstrip("/") + ENDPOINTS["chat"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    tools = [{
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    }]

    payload = {
        "model": Models.LLM,
        "messages": [{"role": "user", "content": "Calculate 25 * 4 + 100"}],
        "tools": tools,
        "tool_choice": "auto",
        "stream": True,
        "tool_stream": True,  # GLM-4.7: Enable streaming tool parameters
        "temperature": Defaults.TEMPERATURE
    }

    console.print("[bold]Request with tool_stream=True:[/bold]")
    syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
    console.print(syntax)

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=HTTP_TIMEOUT_STREAMING)
        response.raise_for_status()

        console.print("\n[bold]Streaming tool arguments:[/bold]")

        # Concatenate tool arguments across chunks (GLM-4.7 pattern)
        tool_calls = {}

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data:"):
                    data_str = line_str[5:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})

                            # Handle streaming tool calls
                            if "tool_calls" in delta:
                                for tc in delta["tool_calls"]:
                                    idx = tc.get("index", 0)
                                    if idx not in tool_calls:
                                        tool_calls[idx] = {
                                            "id": tc.get("id"),
                                            "function": {
                                                "name": tc.get("function", {}).get("name", ""),
                                                "arguments": tc.get("function", {}).get("arguments", "")
                                            }
                                        }
                                        if tool_calls[idx]["function"]["name"]:
                                            console.print(f"[dim]Tool: {tool_calls[idx]['function']['name']}[/dim]")
                                    else:
                                        # Concatenate arguments
                                        args = tc.get("function", {}).get("arguments", "")
                                        if args:
                                            tool_calls[idx]["function"]["arguments"] += args
                                            console.print(f"[dim]+{args}[/dim]", end="")
                    except json.JSONDecodeError:
                        pass

        console.print("\n\n[bold]Final Tool Calls:[/bold]")
        syntax = Syntax(json.dumps(tool_calls, indent=2), "json", theme="monokai")
        console.print(syntax)

        return tool_calls

    except Exception as e:
        console.print(f"[red]Error ({type(e).__name__}): {e}[/red]")
        return None


def show_curl_examples():
    """Show equivalent curl commands."""
    console.print(Panel.fit(
        "[bold cyan]Curl Examples[/bold cyan]\n"
        "Equivalent curl commands for the API",
        border_style="cyan"
    ))

    full_url = BASE_URL.rstrip("/") + ENDPOINTS["chat"]
    examples = [
        {
            "name": "Basic Chat with Parameters",
            "curl": f'''curl -X POST "{full_url}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.LLM}",
    "messages": [{{"role": "user", "content": "Hello!"}}],
    "temperature": 1.0,
    "max_tokens": 4096
  }}'
'''
        },
        {
            "name": "Streaming with Thinking",
            "curl": f'''curl -X POST "{full_url}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.LLM}",
    "messages": [{{"role": "user", "content": "Tell me a story"}}],
    "stream": true,
    "thinking": {{"type": "enabled"}},
    "temperature": 1.0
  }}'
'''
        },
        {
            "name": "Streaming Tool Calls (tool_stream)",
            "curl": f'''curl -X POST "{full_url}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.LLM}",
    "messages": [{{"role": "user", "content": "Calculate 100 * 5"}}],
    "tools": [{{"type": "function", "function": {{"name": "calculate", "parameters": {{"type": "object", "properties": {{"expression": {{"type": "string"}}}}}}}}}}],
    "stream": true,
    "tool_stream": true,
    "temperature": 1.0
  }}'
'''
        }
    ]

    for example in examples:
        console.print(f"\n[bold]{example['name']}:[/bold]")
        syntax = Syntax(example["curl"], "bash", theme="monokai")
        console.print(syntax)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTP Chat Completion Example")
    parser.add_argument("-p", "--prompt", type=str, help="Chat prompt")
    parser.add_argument("--stream", action="store_true", help="Enable streaming")
    parser.add_argument("--demo-thinking", action="store_true",
                        help="Demo thinking mode")
    parser.add_argument("--demo-tools", action="store_true",
                        help="Demo function calling")
    parser.add_argument("--demo-streaming-tools", action="store_true",
                        help="Demo streaming tool calls (tool_stream=True)")
    parser.add_argument("--show-curl", action="store_true",
                        help="Show curl examples")

    args = parser.parse_args()

    if args.demo_thinking:
        demo_with_thinking()
    elif args.demo_tools:
        demo_with_tools()
    elif args.demo_streaming_tools:
        demo_streaming_tool_calls()
    elif args.show_curl:
        show_curl_examples()
    else:
        run(prompt=args.prompt, stream=args.stream)
