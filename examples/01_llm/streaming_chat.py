"""
Streaming Chat Example
Demonstrates streaming chat completion with real-time token output.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown

from config import Models, TEST_PROMPTS, Defaults
from utils.client import get_client, print_error

console = Console()


def run(custom_prompt: str = None, show_reasoning: bool = True):
    """
    Run a streaming chat completion with real-time output.

    Args:
        custom_prompt: Optional custom prompt
        show_reasoning: Whether to show reasoning content if present
    """
    console.print(Panel.fit(
        "[bold cyan]Streaming Chat Example[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Watch the response stream in real-time!",
        border_style="cyan"
    ))

    prompt = custom_prompt or TEST_PROMPTS["coding"]
    console.print(f"\n[bold]Prompt:[/bold] {prompt}\n")

    try:
        client = get_client()

        console.print("[dim]Streaming response...[/dim]\n")

        # Create streaming chat completion
        response = client.create_chat(
            messages=[
                {"role": "system", "content": "You are an expert programmer."},
                {"role": "user", "content": prompt}
            ],
            model=Models.LLM,
            stream=True,
            temperature=Defaults.TEMPERATURE,  # GLM-4.7 best practice
            thinking={"type": "enabled"}  # Enable thinking to show reasoning
        )

        # Collect the full response
        full_content = ""
        full_reasoning = ""

        console.print("[bold green]Response:[/bold green]")

        # Stream the response
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                # Handle reasoning content (thinking)
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    full_reasoning += delta.reasoning_content
                    if show_reasoning:
                        console.print(f"[dim blue]{escape(delta.reasoning_content)}[/dim blue]", end="")

                # Handle regular content
                if hasattr(delta, "content") and delta.content:
                    full_content += delta.content
                    console.print(delta.content, end="", markup=False)

        console.print("\n")  # New line after streaming

        # Render the full response as Markdown
        if full_content:
            console.print(Panel(
                Markdown(full_content),
                title="Response (Rendered)",
                border_style="green"
            ))

        # Show summary
        if full_reasoning and show_reasoning:
            console.print(Panel(
                Markdown(full_reasoning),
                title="Thinking Summary",
                border_style="blue"
            ))

        console.print(f"[dim]Response length: {len(full_content)} characters[/dim]")

        return {"content": full_content, "reasoning": full_reasoning}

    except Exception as e:
        print_error(e, "Streaming chat failed")
        return None


def demo_code_generation():
    """Demo: Generate code with streaming output."""
    prompts = [
        "Write a Python function to find the longest palindromic substring.",
        "Create a TypeScript interface for a REST API response with pagination.",
        "Write a SQL query to find the top 10 customers by total order value.",
    ]

    console.print(Panel.fit(
        "[bold cyan]Code Generation Demo[/bold cyan]\n"
        "Generating code with multiple prompts...",
        border_style="cyan"
    ))

    for i, prompt in enumerate(prompts, 1):
        console.print(f"\n[bold]Example {i}/{len(prompts)}[/bold]")
        console.rule()
        run(custom_prompt=prompt, show_reasoning=False)
        console.print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Streaming Chat Example")
    parser.add_argument("-p", "--prompt", type=str,
                        help="Custom prompt to use")
    parser.add_argument("--no-reasoning", action="store_true",
                        help="Hide reasoning/thinking output")
    parser.add_argument("--demo", action="store_true",
                        help="Run code generation demo")

    args = parser.parse_args()

    if args.demo:
        demo_code_generation()
    else:
        run(custom_prompt=args.prompt, show_reasoning=not args.no_reasoning)
