"""
Web Search in Chat Example
Demonstrates using web search as a tool within chat completions.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from config import Models
from utils.client import get_client, print_error

console = Console()

# Web search tool definition
WEB_SEARCH_TOOL = {
    "type": "web_search",
    "web_search": {
        "enable": "True",
        "search_engine": "search-prime",
        "search_result": "True",
        "count": "5"
    }
}


def run(query: str = None, stream: bool = True):
    """
    Chat with web search enabled, allowing the model to search for information.

    Args:
        query: User's question that may require web search
        stream: Whether to stream the response
    """
    console.print(Panel.fit(
        "[bold cyan]Web Search in Chat[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Chat with integrated web search capability",
        border_style="cyan"
    ))

    query = query or "What are the latest developments in large language models?"

    console.print(f"\n[bold]User Query:[/bold] {query}\n")

    try:
        client = get_client()

        messages = [{"role": "user", "content": query}]

        console.print("[dim]Searching and generating response...[/dim]\n")

        if stream:
            response = client.create_chat(
                messages=messages,
                tools=[WEB_SEARCH_TOOL],
                stream=True
            )

            result = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        result += delta.content
                        console.print(delta.content, end="", markup=False)

            console.print("\n")

        else:
            response = client.create_chat(
                messages=messages,
                tools=[WEB_SEARCH_TOOL]
            )

            result = response.choices[0].message.content
            console.print(Panel(
                Markdown(result),
                title="Response",
                border_style="green"
            ))

        return {"query": query, "response": result}

    except Exception as e:
        print_error(e, "Web search chat failed")
        return None


def demo_research_assistant():
    """Demo: Multi-turn research conversation with web search."""
    console.print(Panel.fit(
        "[bold cyan]Research Assistant Demo[/bold cyan]\n"
        "Multi-turn conversation with web search",
        border_style="cyan"
    ))

    try:
        client = get_client()

        # Research conversation
        conversation = [
            "What is quantum computing and how does it differ from classical computing?",
            "What companies are leading in quantum computing development?",
            "What are the main challenges in building practical quantum computers?"
        ]

        messages = []

        for i, query in enumerate(conversation, 1):
            console.print(f"\n[bold]Question {i}:[/bold] {query}")
            console.rule()

            messages.append({"role": "user", "content": query})

            response = client.create_chat(
                messages=messages,
                tools=[WEB_SEARCH_TOOL]
            )

            assistant_content = response.choices[0].message.content
            messages.append({"role": "assistant", "content": assistant_content})

            console.print(Panel(
                Markdown(assistant_content[:500] + "..." if len(assistant_content) > 500 else assistant_content),
                title="Response",
                border_style="green"
            ))

        return messages

    except Exception as e:
        print_error(e, "Research assistant demo failed")
        return None


def demo_fact_checking():
    """Demo: Using web search to verify claims."""
    console.print(Panel.fit(
        "[bold cyan]Fact Checking Demo[/bold cyan]\n"
        "Verifying claims with web search",
        border_style="cyan"
    ))

    claims = [
        "The Eiffel Tower is the tallest structure in France",
        "Python was created in 1991 by Guido van Rossum",
        "There are 8 planets in our solar system",
    ]

    try:
        client = get_client()

        results = []
        for claim in claims:
            console.print(f"\n[bold]Claim:[/bold] {claim}")

            prompt = f"""Verify this claim using web search:
"{claim}"

Provide:
1. Whether the claim is TRUE, FALSE, or PARTIALLY TRUE
2. The correct information if the claim is inaccurate
3. Sources for your verification"""

            response = client.create_chat(
                messages=[{"role": "user", "content": prompt}],
                tools=[WEB_SEARCH_TOOL]
            )

            result = response.choices[0].message.content
            console.print(Panel(
                Markdown(result),
                title="Verification",
                border_style="yellow"
            ))

            results.append({"claim": claim, "verification": result})

        return results

    except Exception as e:
        print_error(e, "Fact checking demo failed")
        return None


def demo_current_events():
    """Demo: Getting current information about recent events."""
    console.print(Panel.fit(
        "[bold cyan]Current Events Demo[/bold cyan]\n"
        "Accessing up-to-date information",
        border_style="cyan"
    ))

    topics = [
        "What are the top tech news stories today?",
        "What is the current state of the global economy?",
        "What are the latest developments in renewable energy?",
    ]

    try:
        client = get_client()

        results = []
        for topic in topics:
            console.print(f"\n[bold]Topic:[/bold] {topic}")
            console.rule()

            response = client.create_chat(
                messages=[{"role": "user", "content": topic}],
                tools=[WEB_SEARCH_TOOL]
            )

            result = response.choices[0].message.content
            console.print(Panel(
                Markdown(result[:600] + "..." if len(result) > 600 else result),
                title="Current Information",
                border_style="green"
            ))

            results.append({"topic": topic, "response": result})

        return results

    except Exception as e:
        print_error(e, "Current events demo failed")
        return None


def demo_with_custom_search_params():
    """Demo: Customizing web search parameters."""
    console.print(Panel.fit(
        "[bold cyan]Custom Search Parameters Demo[/bold cyan]\n"
        "Fine-tuning web search behavior",
        border_style="cyan"
    ))

    # Different search configurations
    configs = [
        {
            "name": "Minimal Results",
            "tool": {
                "type": "web_search",
                "web_search": {
                    "enable": "True",
                    "search_engine": "search-prime",
                    "count": "2"
                }
            }
        },
        {
            "name": "Maximum Results",
            "tool": {
                "type": "web_search",
                "web_search": {
                    "enable": "True",
                    "search_engine": "search-prime",
                    "count": "10",
                    "search_result": "True"
                }
            }
        }
    ]

    query = "What is the current population of Tokyo?"

    try:
        client = get_client()

        for config in configs:
            console.print(f"\n[bold]Configuration:[/bold] {config['name']}")
            console.print(f"[dim]Count: {config['tool']['web_search'].get('count', 'default')}[/dim]")

            response = client.create_chat(
                messages=[{"role": "user", "content": query}],
                tools=[config["tool"]]
            )

            result = response.choices[0].message.content
            console.print(Panel(
                result,
                title="Response",
                border_style="green"
            ))

    except Exception as e:
        print_error(e, "Custom search params demo failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web Search in Chat Example")
    parser.add_argument("-q", "--query", type=str, help="Question to ask")
    parser.add_argument("--no-stream", action="store_true",
                        help="Disable streaming")
    parser.add_argument("--demo-research", action="store_true",
                        help="Run research assistant demo")
    parser.add_argument("--demo-factcheck", action="store_true",
                        help="Run fact checking demo")
    parser.add_argument("--demo-events", action="store_true",
                        help="Run current events demo")
    parser.add_argument("--demo-custom", action="store_true",
                        help="Run custom parameters demo")

    args = parser.parse_args()

    if args.demo_research:
        demo_research_assistant()
    elif args.demo_factcheck:
        demo_fact_checking()
    elif args.demo_events:
        demo_current_events()
    elif args.demo_custom:
        demo_with_custom_search_params()
    else:
        run(query=args.query, stream=not args.no_stream)
