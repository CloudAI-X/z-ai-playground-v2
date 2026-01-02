"""
Image Understanding Example
Demonstrates GLM-4.6V's ability to analyze and describe images.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from config import Models, get_sample_images, TEST_PROMPTS
from utils.client import get_client, print_error

console = Console()


def run(image_url: str = None, prompt: str = None, stream: bool = True):
    """
    Analyze an image using GLM-4.6V.

    Args:
        image_url: URL of the image to analyze (uses sample if not provided)
        prompt: Question/instruction about the image
        stream: Whether to stream the response
    """
    console.print(Panel.fit(
        "[bold cyan]Image Understanding Example[/bold cyan]\n"
        f"Model: {Models.VLM}\n"
        "Analyzing images with vision-language capabilities",
        border_style="cyan"
    ))

    # Use defaults if not provided
    image_url = image_url or get_sample_images()[0]
    prompt = prompt or TEST_PROMPTS["vision"]

    console.print(f"\n[bold]Image URL:[/bold] {image_url[:80]}...")
    console.print(f"[bold]Prompt:[/bold] {prompt}\n")

    try:
        client = get_client()

        # Construct multimodal message
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": image_url}
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]

        console.print("[dim]Analyzing image...[/dim]\n")

        if stream:
            response = client.create_chat(
                messages=messages,
                model=Models.VLM,
                stream=True,
                thinking={"type": "enabled"}
            )

            reasoning = ""
            content = ""

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta

                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        reasoning += delta.reasoning_content

                    if hasattr(delta, "content") and delta.content:
                        content += delta.content
                        console.print(delta.content, end="", markup=False)

            console.print("\n")

            # Render the full response as Markdown
            if content:
                console.print(Panel(
                    Markdown(content),
                    title="Analysis (Rendered)",
                    border_style="green"
                ))

            if reasoning:
                console.print(Panel(
                    Markdown(reasoning),
                    title="Model Reasoning",
                    border_style="blue"
                ))

            return {"content": content, "reasoning": reasoning}

        else:
            response = client.create_chat(
                messages=messages,
                model=Models.VLM,
                thinking={"type": "enabled"}
            )

            content = response.choices[0].message.content
            console.print(Panel(Markdown(content), title="Analysis", border_style="green"))

            return {"content": content}

    except Exception as e:
        print_error(e, "Image analysis failed")
        return None


def analyze_multiple_aspects(image_url: str = None):
    """Analyze an image from multiple perspectives."""
    console.print(Panel.fit(
        "[bold cyan]Multi-Aspect Image Analysis[/bold cyan]\n"
        "Analyzing the same image with different prompts",
        border_style="cyan"
    ))

    image_url = image_url or get_sample_images()[0]

    aspects = [
        ("Description", "Describe this image in detail."),
        ("Objects", "List all objects visible in this image."),
        ("Colors", "What are the dominant colors in this image?"),
        ("Mood", "What mood or atmosphere does this image convey?"),
    ]

    results = {}

    for aspect_name, prompt in aspects:
        console.print(f"\n[bold]{aspect_name}:[/bold]")
        result = run(image_url=image_url, prompt=prompt, stream=False)
        if result:
            results[aspect_name] = result["content"]

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Understanding Example")
    parser.add_argument("-u", "--url", type=str, help="Image URL to analyze")
    parser.add_argument("-p", "--prompt", type=str, help="Custom prompt")
    parser.add_argument("--multi-aspect", action="store_true",
                        help="Analyze image from multiple perspectives")
    parser.add_argument("--no-stream", action="store_true",
                        help="Disable streaming output")

    args = parser.parse_args()

    if args.multi_aspect:
        analyze_multiple_aspects(image_url=args.url)
    else:
        run(image_url=args.url, prompt=args.prompt, stream=not args.no_stream)
