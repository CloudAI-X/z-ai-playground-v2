"""
Basic Chat Example
Demonstrates simple single-turn chat completion with GLM-5.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from config import Models, TEST_PROMPTS, Defaults
from utils.client import get_client, print_response, print_error

console = Console()


def run(custom_prompt: str = None):
    """
    Run a basic single-turn chat completion.

    Args:
        custom_prompt: Optional custom prompt (uses default if not provided)
    """
    console.print(Panel.fit(
        "[bold cyan]Basic Chat Example[/bold cyan]\n"
        f"Model: {Models.LLM}",
        border_style="cyan"
    ))

    # Get prompt
    prompt = custom_prompt or TEST_PROMPTS["chat"]
    console.print(f"\n[bold]Prompt:[/bold] {prompt}\n")

    try:
        # Get client
        client = get_client()

        # Create chat completion
        console.print("[dim]Sending request...[/dim]\n")

        response = client.create_chat(
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            model=Models.LLM,
            temperature=Defaults.TEMPERATURE,  # GLM-5 best practice
            thinking={"type": "disabled"}  # Disable thinking for basic example
        )

        # Print response
        print_response(response, title="AI Response")

        return response

    except Exception as e:
        print_error(e, "Chat completion failed")
        return None


def interactive():
    """Run interactive mode where user can enter custom prompts."""
    console.print(Panel.fit(
        "[bold cyan]Interactive Chat Mode[/bold cyan]\n"
        "Type your message and press Enter.\n"
        "Type 'quit' to exit.",
        border_style="cyan"
    ))

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            if user_input.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break

            if not user_input.strip():
                continue

            run(custom_prompt=user_input)

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Basic Chat Example")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("-p", "--prompt", type=str,
                        help="Custom prompt to use")

    args = parser.parse_args()

    if args.interactive:
        interactive()
    else:
        run(custom_prompt=args.prompt)
