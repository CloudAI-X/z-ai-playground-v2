"""
Structured Output Example
Demonstrates GLM-5's ability to return structured JSON responses.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from config import Models
from utils.client import get_client, print_error

console = Console()


def run(prompt: str = None, schema_type: str = "product"):
    """
    Get structured JSON output from GLM-5.

    Args:
        prompt: The prompt to send
        schema_type: Type of schema to request (product, person, event)
    """
    console.print(Panel.fit(
        "[bold cyan]Structured Output Example[/bold cyan]\n"
        f"Model: {Models.LLM}\n"
        "Getting JSON-formatted responses",
        border_style="cyan"
    ))

    # Different example prompts and expected structures
    examples = {
        "product": {
            "prompt": "Generate a product listing for a high-end wireless headphone.",
            "schema_hint": """Return a JSON object with:
- name: product name
- price: price in USD (number)
- category: product category
- features: array of feature strings
- specifications: object with tech specs
- rating: number from 1-5"""
        },
        "person": {
            "prompt": "Create a fictional character profile for a detective in a mystery novel.",
            "schema_hint": """Return a JSON object with:
- name: full name
- age: number
- occupation: job title
- background: brief history
- skills: array of abilities
- personality_traits: array of traits"""
        },
        "event": {
            "prompt": "Generate details for a tech conference event.",
            "schema_hint": """Return a JSON object with:
- name: event name
- date: event date (YYYY-MM-DD)
- location: venue and city
- description: brief description
- speakers: array of speaker objects (name, topic)
- ticket_price: number"""
        }
    }

    example = examples.get(schema_type, examples["product"])
    prompt = prompt or example["prompt"]
    schema_hint = example["schema_hint"]

    console.print(f"\n[bold]Schema Type:[/bold] {schema_type}")
    console.print(f"[bold]Prompt:[/bold] {prompt}\n")

    full_prompt = f"""{prompt}

{schema_hint}

Return ONLY valid JSON, no other text."""

    try:
        client = get_client()

        console.print("[dim]Requesting structured output...[/dim]\n")

        response = client.create_chat(
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        # Try to parse the JSON
        try:
            # Handle potential markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            parsed = json.loads(content)

            # Pretty print the JSON
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            syntax = Syntax(formatted, "json", theme="monokai", line_numbers=True)

            console.print(Panel(
                syntax,
                title="Structured Output",
                border_style="green"
            ))

            return parsed

        except json.JSONDecodeError as e:
            console.print("[yellow]Could not parse as JSON:[/yellow]")
            console.print(f"[red]Error: {e}[/red]")
            console.print(Panel(content, title="Raw Response", border_style="yellow"))
            return content

    except Exception as e:
        print_error(e, "Structured output failed")
        return None


def demo_data_extraction():
    """Demo: Extract structured data from unstructured text."""
    console.print(Panel.fit(
        "[bold cyan]Data Extraction Demo[/bold cyan]\n"
        "Extracting structured data from text",
        border_style="cyan"
    ))

    unstructured_text = """
    Hi, I'm looking for help with my order. My name is Sarah Johnson and you can
    reach me at sarah.j@email.com or call me at 555-0123. I ordered a Blue Widget
    (SKU: BW-12345) on January 15th, 2024 for $49.99 but it arrived damaged.
    My order number is ORD-98765. I'd like a replacement shipped to
    123 Main Street, Apt 4B, New York, NY 10001.
    """

    prompt = f"""Extract all relevant information from this customer support message:

{unstructured_text}

Return a JSON object with these fields:
- customer: object with name, email, phone
- order: object with order_number, sku, product_name, price, date
- issue: description of the problem
- requested_action: what the customer wants
- shipping_address: object with street, apartment, city, state, zip"""

    try:
        client = get_client()

        response = client.create_chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        parsed = json.loads(content)

        # Display in a formatted way
        console.print(Panel(unstructured_text.strip(), title="Original Text", border_style="blue"))
        console.print()

        formatted = json.dumps(parsed, indent=2)
        syntax = Syntax(formatted, "json", theme="monokai")
        console.print(Panel(syntax, title="Extracted Data", border_style="green"))

        return parsed

    except Exception as e:
        print_error(e, "Data extraction failed")
        return None


def demo_list_generation():
    """Demo: Generate structured lists."""
    console.print(Panel.fit(
        "[bold cyan]List Generation Demo[/bold cyan]\n"
        "Generating structured arrays",
        border_style="cyan"
    ))

    prompts = [
        {
            "title": "Programming Languages",
            "prompt": """List 5 programming languages with details.
Return a JSON object with "languages" array, each item having:
- name, year_created, creator, primary_use, difficulty (beginner/intermediate/advanced)"""
        },
        {
            "title": "Recipes",
            "prompt": """Create 3 simple recipes.
Return a JSON object with "recipes" array, each item having:
- name, prep_time_minutes, servings, ingredients (array), steps (array)"""
        }
    ]

    results = []
    for item in prompts:
        console.print(f"\n[bold]{item['title']}:[/bold]")

        try:
            client = get_client()

            response = client.create_chat(
                messages=[{"role": "user", "content": item["prompt"]}],
                response_format={"type": "json_object"}
            )

            parsed = json.loads(response.choices[0].message.content)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            syntax = Syntax(formatted, "json", theme="monokai")
            console.print(Panel(syntax, border_style="green"))

            results.append(parsed)

        except Exception as e:
            print_error(e, f"Failed to generate {item['title']}")

    return results


def demo_schema_validation():
    """Demo: Validate response against expected schema."""
    console.print(Panel.fit(
        "[bold cyan]Schema Validation Demo[/bold cyan]\n"
        "Ensuring output matches expected structure",
        border_style="cyan"
    ))

    # Define expected schema
    expected_schema = {
        "type": "object",
        "required": ["title", "author", "year", "genre", "rating"],
        "properties": {
            "title": {"type": "string"},
            "author": {"type": "string"},
            "year": {"type": "integer"},
            "genre": {"type": "string"},
            "rating": {"type": "number", "minimum": 0, "maximum": 5}
        }
    }

    prompt = """Create a fictional book entry.
Return JSON with: title, author, year (integer), genre, rating (number 0-5)"""

    try:
        client = get_client()

        response = client.create_chat(
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        parsed = json.loads(response.choices[0].message.content)

        # Simple validation
        validation_results = []
        for field in expected_schema["required"]:
            present = field in parsed
            validation_results.append((field, present, type(parsed.get(field)).__name__))

        # Display results
        table = Table(title="Schema Validation")
        table.add_column("Field", style="cyan")
        table.add_column("Present", style="white")
        table.add_column("Type", style="yellow")

        for field, present, type_name in validation_results:
            status = "[green]✓[/green]" if present else "[red]✗[/red]"
            table.add_row(field, status, type_name)

        console.print(table)

        formatted = json.dumps(parsed, indent=2)
        syntax = Syntax(formatted, "json", theme="monokai")
        console.print(Panel(syntax, title="Generated Data", border_style="green"))

        return parsed

    except Exception as e:
        print_error(e, "Schema validation demo failed")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Structured Output Example")
    parser.add_argument("-p", "--prompt", type=str, help="Custom prompt")
    parser.add_argument("-s", "--schema", type=str, default="product",
                        choices=["product", "person", "event"],
                        help="Schema type to use")
    parser.add_argument("--demo-extraction", action="store_true",
                        help="Run data extraction demo")
    parser.add_argument("--demo-lists", action="store_true",
                        help="Run list generation demo")
    parser.add_argument("--demo-validation", action="store_true",
                        help="Run schema validation demo")

    args = parser.parse_args()

    if args.demo_extraction:
        demo_data_extraction()
    elif args.demo_lists:
        demo_list_generation()
    elif args.demo_validation:
        demo_schema_validation()
    else:
        run(prompt=args.prompt, schema_type=args.schema)
