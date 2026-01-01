"""
Web Search API Example
Demonstrates direct web search using Z.AI's search-prime engine.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from utils.client import get_client, print_error

console = Console()


def run(query: str = None, count: int = 5, domain_filter: str = None):
    """
    Perform a web search using Z.AI's search API.

    Args:
        query: Search query
        count: Number of results to return (max 15)
        domain_filter: Optional domain to filter results
    """
    console.print(Panel.fit(
        "[bold cyan]Web Search API Example[/bold cyan]\n"
        "Direct web search with search-prime engine",
        border_style="cyan"
    ))

    query = query or "Latest developments in AI 2024"

    console.print(f"\n[bold]Query:[/bold] {query}")
    console.print(f"[bold]Results:[/bold] {count}")
    if domain_filter:
        console.print(f"[bold]Domain Filter:[/bold] {domain_filter}")
    console.print()

    try:
        client = get_client()

        console.print("[dim]Searching...[/dim]\n")

        # Perform web search
        kwargs = {
            "search_query": query,
            "count": min(count, 15),
            "search_recency_filter": "noLimit"
        }

        if domain_filter:
            kwargs["search_domain_filter"] = domain_filter

        response = client.client.web_search.web_search(
            search_engine="search-prime",
            **kwargs
        )

        # Display results
        if hasattr(response, "search_result") and response.search_result:
            results = response.search_result

            console.print(f"[green]Found {len(results)} results[/green]\n")

            for i, result in enumerate(results, 1):
                title = getattr(result, "title", "No title")
                link = getattr(result, "link", "No link")
                content = getattr(result, "content", "No content")[:200]
                media = getattr(result, "media", None)

                console.print(Panel(
                    f"[bold]{title}[/bold]\n\n"
                    f"[blue]{link}[/blue]\n\n"
                    f"{content}...",
                    title=f"Result {i}",
                    border_style="green"
                ))

            return results

        else:
            console.print("[yellow]No results found[/yellow]")
            return []

    except Exception as e:
        print_error(e, "Web search failed")
        return None


def demo_filtered_search():
    """Demo: Search with domain filtering."""
    console.print(Panel.fit(
        "[bold cyan]Filtered Search Demo[/bold cyan]\n"
        "Searching within specific domains",
        border_style="cyan"
    ))

    searches = [
        ("Python tutorials", "python.org", 3),
        ("Machine learning papers", "arxiv.org", 3),
        ("TypeScript documentation", "typescriptlang.org", 3),
    ]

    results = []
    for query, domain, count in searches:
        console.print(f"\n[bold]Search:[/bold] {query} (on {domain})")
        console.rule()
        result = run(query=query, count=count, domain_filter=domain)
        if result:
            results.extend(result)

    return results


def demo_recency_search():
    """Demo: Search with recency filters."""
    console.print(Panel.fit(
        "[bold cyan]Recency Search Demo[/bold cyan]\n"
        "Finding recent content",
        border_style="cyan"
    ))

    console.print("""
[yellow]Available recency filters:[/yellow]
- noLimit: All time
- day: Past 24 hours
- week: Past week
- month: Past month
- year: Past year

[dim]Note: The default is 'noLimit'[/dim]
""")

    # Search for recent news
    query = "artificial intelligence breakthroughs"
    console.print(f"\n[bold]Searching for:[/bold] {query}")

    try:
        client = get_client()

        response = client.client.web_search.web_search(
            search_engine="search-prime",
            search_query=query,
            count=5,
            search_recency_filter="month"  # Past month
        )

        if hasattr(response, "search_result") and response.search_result:
            results = response.search_result

            table = Table(title="Recent Results (Past Month)")
            table.add_column("#", style="cyan", width=3)
            table.add_column("Title", style="white", width=50)
            table.add_column("Source", style="blue")

            for i, result in enumerate(results, 1):
                title = getattr(result, "title", "No title")[:50]
                link = getattr(result, "link", "")
                # Extract domain from link
                domain = link.split("/")[2] if len(link.split("/")) > 2 else link
                table.add_row(str(i), title, domain)

            console.print(table)
            return results

    except Exception as e:
        print_error(e, "Recency search failed")

    return None


def demo_comprehensive_search():
    """Demo: Comprehensive search with all options."""
    console.print(Panel.fit(
        "[bold cyan]Comprehensive Search Demo[/bold cyan]\n"
        "Using all search options together",
        border_style="cyan"
    ))

    query = "Claude AI capabilities"

    console.print(f"\n[bold]Query:[/bold] {query}")
    console.print("[bold]Options:[/bold]")
    console.print("  - Engine: search-prime")
    console.print("  - Count: 10")
    console.print("  - Recency: Past year")
    console.print()

    try:
        client = get_client()

        response = client.client.web_search.web_search(
            search_engine="search-prime",
            search_query=query,
            count=10,
            search_recency_filter="year"
        )

        if hasattr(response, "search_result") and response.search_result:
            results = response.search_result

            console.print(f"[green]Found {len(results)} results[/green]\n")

            # Detailed display
            for i, result in enumerate(results[:5], 1):  # Show first 5
                title = getattr(result, "title", "No title")
                link = getattr(result, "link", "No link")
                content = getattr(result, "content", "")

                console.print(f"[bold cyan]{i}. {title}[/bold cyan]")
                console.print(f"   [blue underline]{link}[/blue underline]")
                if content:
                    console.print(f"   [dim]{content[:150]}...[/dim]")
                console.print()

            if len(results) > 5:
                console.print(f"[dim]... and {len(results) - 5} more results[/dim]")

            return results

    except Exception as e:
        print_error(e, "Comprehensive search failed")

    return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Web Search API Example")
    parser.add_argument("-q", "--query", type=str, help="Search query")
    parser.add_argument("-n", "--count", type=int, default=5,
                        help="Number of results (max 15)")
    parser.add_argument("-d", "--domain", type=str,
                        help="Domain filter")
    parser.add_argument("--demo-filtered", action="store_true",
                        help="Run filtered search demo")
    parser.add_argument("--demo-recency", action="store_true",
                        help="Run recency search demo")
    parser.add_argument("--demo-comprehensive", action="store_true",
                        help="Run comprehensive search demo")

    args = parser.parse_args()

    if args.demo_filtered:
        demo_filtered_search()
    elif args.demo_recency:
        demo_recency_search()
    elif args.demo_comprehensive:
        demo_comprehensive_search()
    else:
        run(query=args.query, count=args.count, domain_filter=args.domain)
