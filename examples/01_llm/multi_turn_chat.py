"""
Multi-turn Conversation Example
Demonstrates maintaining conversation history across multiple turns.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from config import Models
from utils.client import get_client, print_response, print_error

console = Console()


class Conversation:
    """Manages a multi-turn conversation with context."""

    def __init__(self, system_prompt: str = None):
        self.client = get_client()
        self.messages = []

        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })

    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation."""
        self.messages.append({"role": "assistant", "content": content})

    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response, maintaining context.

        Args:
            user_message: The user's message

        Returns:
            The assistant's response content
        """
        self.add_user_message(user_message)

        response = self.client.create_chat(
            messages=self.messages,
            model=Models.LLM,
            thinking={"type": "disabled"}
        )

        assistant_content = response.choices[0].message.content
        self.add_assistant_message(assistant_content)

        return assistant_content

    def show_history(self):
        """Display the conversation history."""
        table = Table(title="Conversation History")
        table.add_column("Role", style="cyan")
        table.add_column("Content", style="white")

        for msg in self.messages:
            role = msg["role"].capitalize()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            table.add_row(role, content)

        console.print(table)

    def clear(self):
        """Clear conversation history (keeping system prompt if any)."""
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        self.messages = system_msgs


def run():
    """Run a scripted multi-turn conversation demo."""
    console.print(Panel.fit(
        "[bold cyan]Multi-turn Conversation Example[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Demonstrates context maintained across turns.",
        border_style="cyan"
    ))

    # Create conversation with system prompt
    conv = Conversation(
        system_prompt="You are a helpful AI tutor specializing in explaining "
                      "complex topics in simple terms. Be concise but thorough."
    )

    # Scripted conversation
    turns = [
        "What is machine learning?",
        "Can you give me a simple real-world example?",
        "How is deep learning different from regular machine learning?",
        "What would I need to learn to get started with ML?",
    ]

    console.print("\n[bold]Starting multi-turn conversation...[/bold]\n")

    try:
        for i, message in enumerate(turns, 1):
            console.print(f"[bold green]Turn {i} - You:[/bold green] {message}")
            console.print()

            response = conv.chat(message)

            console.print(Panel(
                Markdown(response),
                title=f"AI Response (Turn {i})",
                border_style="cyan"
            ))
            console.print()

        # Show final history
        console.print("\n[bold]Conversation Summary:[/bold]")
        conv.show_history()

    except Exception as e:
        print_error(e, "Conversation failed")


def interactive():
    """Run an interactive multi-turn conversation."""
    console.print(Panel.fit(
        "[bold cyan]Interactive Multi-turn Chat[/bold cyan]\n"
        "Type your messages to have a conversation.\n"
        "Commands: 'history' - show history, 'clear' - clear history, 'quit' - exit",
        border_style="cyan"
    ))

    # Get optional system prompt
    system = Prompt.ask(
        "\n[dim]Enter system prompt (or press Enter for default)[/dim]",
        default="You are a helpful AI assistant."
    )

    conv = Conversation(system_prompt=system)
    console.print("\n[dim]Conversation started. Type your message.[/dim]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            cmd = user_input.lower().strip()

            if cmd in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break
            elif cmd == "history":
                conv.show_history()
                continue
            elif cmd == "clear":
                conv.clear()
                console.print("[dim]Conversation cleared.[/dim]")
                continue

            response = conv.chat(user_input)
            console.print(Panel(Markdown(response), title="AI", border_style="cyan"))

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Goodbye![/dim]")
            break
        except Exception as e:
            print_error(e, "Error")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-turn Conversation Example")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode")

    args = parser.parse_args()

    if args.interactive:
        interactive()
    else:
        run()
