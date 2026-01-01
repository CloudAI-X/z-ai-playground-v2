"""
HTTP Image Generation Example
Demonstrates direct HTTP API calls for CogView-4 image generation.
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

from config import API_KEY, ENDPOINTS, Models, TEST_PROMPTS

console = Console()


def run(prompt: str = None, size: str = "1024x1024"):
    """
    Make a direct HTTP API call for image generation.

    Args:
        prompt: Image description
        size: Image dimensions
    """
    console.print(Panel.fit(
        "[bold cyan]HTTP Image Generation[/bold cyan]\n"
        f"Model: {Models.IMAGE_GEN}\n"
        "Direct API call without SDK",
        border_style="cyan"
    ))

    prompt = prompt or TEST_PROMPTS["image_gen"]

    console.print(f"\n[bold]Prompt:[/bold] {prompt}")
    console.print(f"[bold]Size:[/bold] {size}\n")

    # Prepare request
    url = ENDPOINTS["image_generation"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Models.IMAGE_GEN,
        "prompt": prompt,
        "size": size
    }

    # Show the request
    console.print("[bold]Request:[/bold]")
    syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
    console.print(syntax)
    console.print()

    try:
        console.print("[dim]Sending request...[/dim]\n")

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        # Display response
        console.print("[bold]Response:[/bold]")
        syntax = Syntax(json.dumps(result, indent=2, ensure_ascii=False), "json", theme="monokai")
        console.print(syntax)

        # Extract image URL
        if "data" in result and result["data"]:
            image_url = result["data"][0].get("url")
            if image_url:
                console.print(Panel(
                    f"[green]Image generated successfully![/green]\n\n"
                    f"[bold]URL:[/bold] {image_url}",
                    title="Result",
                    border_style="green"
                ))

        return result

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e.response.status_code}[/red]")
        console.print(f"[dim]{e.response.text}[/dim]")
        return None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None


def demo_various_sizes():
    """Demo: Generate images in various sizes."""
    console.print(Panel.fit(
        "[bold cyan]Multi-Size HTTP Demo[/bold cyan]\n"
        "Direct API calls for different sizes",
        border_style="cyan"
    ))

    sizes = ["1024x1024", "1280x720", "768x1344"]
    prompt = "A beautiful sunset over mountains"

    url = ENDPOINTS["image_generation"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    results = []
    for size in sizes:
        console.print(f"\n[bold]Size: {size}[/bold]")

        payload = {
            "model": Models.IMAGE_GEN,
            "prompt": prompt,
            "size": size
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            result = response.json()
            if "data" in result and result["data"]:
                url_str = result["data"][0].get("url", "")
                console.print(f"  [green]Success[/green]: {url_str[:60]}...")
                results.append({"size": size, "url": url_str})
            else:
                console.print(f"  [yellow]No image in response[/yellow]")

        except Exception as e:
            console.print(f"  [red]Error: {e}[/red]")

    return results


def show_curl_examples():
    """Show equivalent curl commands for image generation."""
    console.print(Panel.fit(
        "[bold cyan]Curl Examples[/bold cyan]\n"
        "Image generation curl commands",
        border_style="cyan"
    ))

    examples = [
        {
            "name": "Basic Image Generation",
            "curl": f'''curl -X POST "{ENDPOINTS["image_generation"]}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.IMAGE_GEN}",
    "prompt": "A serene Japanese garden with cherry blossoms",
    "size": "1024x1024"
  }}'
'''
        },
        {
            "name": "HD Landscape Image",
            "curl": f'''curl -X POST "{ENDPOINTS["image_generation"]}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.IMAGE_GEN}",
    "prompt": "Dramatic mountain landscape at sunset, photorealistic",
    "size": "1920x1080"
  }}'
'''
        },
        {
            "name": "Portrait Image",
            "curl": f'''curl -X POST "{ENDPOINTS["image_generation"]}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.IMAGE_GEN}",
    "prompt": "Abstract art, vibrant colors, modern style",
    "size": "768x1344"
  }}'
'''
        }
    ]

    for example in examples:
        console.print(f"\n[bold]{example['name']}:[/bold]")
        syntax = Syntax(example["curl"], "bash", theme="monokai")
        console.print(syntax)


def show_response_structure():
    """Explain the response structure."""
    console.print(Panel.fit(
        "[bold cyan]Response Structure[/bold cyan]\n"
        "Understanding the API response",
        border_style="cyan"
    ))

    sample_response = {
        "created": 1234567890,
        "data": [
            {
                "url": "https://api.z.ai/generated/image_abc123.png"
            }
        ]
    }

    console.print("[bold]Sample Response:[/bold]")
    syntax = Syntax(json.dumps(sample_response, indent=2), "json", theme="monokai")
    console.print(syntax)

    console.print("\n[bold]Fields:[/bold]")
    console.print("  - [cyan]created[/cyan]: Unix timestamp of generation")
    console.print("  - [cyan]data[/cyan]: Array of generated images")
    console.print("  - [cyan]data[].url[/cyan]: Temporary URL to download the image")

    console.print("\n[yellow]Note:[/yellow] URLs are temporary. Download images promptly.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTP Image Generation Example")
    parser.add_argument("-p", "--prompt", type=str, help="Image prompt")
    parser.add_argument("-s", "--size", type=str, default="1024x1024",
                        help="Image size")
    parser.add_argument("--demo-sizes", action="store_true",
                        help="Demo various sizes")
    parser.add_argument("--show-curl", action="store_true",
                        help="Show curl examples")
    parser.add_argument("--show-response", action="store_true",
                        help="Explain response structure")

    args = parser.parse_args()

    if args.demo_sizes:
        demo_various_sizes()
    elif args.show_curl:
        show_curl_examples()
    elif args.show_response:
        show_response_structure()
    else:
        run(prompt=args.prompt, size=args.size)
