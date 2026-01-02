"""
Multi-Image Analysis Example
Demonstrates GLM-4.6V's ability to analyze and compare multiple images.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from config import Models, get_multi_images
from utils.client import get_client, print_error

console = Console()


def run(image_urls: list = None, prompt: str = None):
    """
    Analyze multiple images together using GLM-4.6V.

    Args:
        image_urls: List of image URLs to analyze
        prompt: Question/instruction about the images
    """
    console.print(Panel.fit(
        "[bold cyan]Multi-Image Analysis Example[/bold cyan]\n"
        f"Model: {Models.VLM}\n"
        "Cross-image reasoning and comparison",
        border_style="cyan"
    ))

    # Use sample images if not provided
    image_urls = image_urls or get_multi_images()
    prompt = prompt or "Compare these images. What are the similarities and differences?"

    console.print(f"\n[bold]Analyzing {len(image_urls)} images[/bold]")
    for i, url in enumerate(image_urls, 1):
        console.print(f"  {i}. {url[:60]}...")
    console.print(f"\n[bold]Prompt:[/bold] {prompt}\n")

    try:
        client = get_client()

        # Build content array with multiple images
        content = []

        for url in image_urls:
            content.append({
                "type": "image_url",
                "image_url": {"url": url}
            })

        content.append({
            "type": "text",
            "text": prompt
        })

        messages = [{
            "role": "user",
            "content": content
        }]

        console.print("[dim]Analyzing images...[/dim]\n")

        response = client.create_chat(
            messages=messages,
            model=Models.VLM,
            stream=True,
            thinking={"type": "enabled"}
        )

        reasoning = ""
        result = ""

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta

                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    reasoning += delta.reasoning_content

                if hasattr(delta, "content") and delta.content:
                    result += delta.content
                    console.print(delta.content, end="", markup=False)

        console.print("\n")

        if result:
            console.print(Panel(
                Markdown(result),
                title="Analysis (Rendered)",
                border_style="green"
            ))

        if reasoning:
            console.print(Panel(
                Markdown(reasoning),
                title="Model Reasoning",
                border_style="blue"
            ))

        return {"content": result, "reasoning": reasoning}

    except Exception as e:
        print_error(e, "Multi-image analysis failed")
        return None


def demo_product_comparison():
    """Demo: Compare product images (simulated with sample images)."""
    console.print(Panel.fit(
        "[bold cyan]Product Comparison Demo[/bold cyan]\n"
        "Comparing multiple product images",
        border_style="cyan"
    ))

    # Use sample images as stand-ins
    image_urls = get_multi_images()

    prompts = [
        "Which of these products looks more premium? Explain your reasoning.",
        "If these were products on a shopping site, which would you recommend and why?",
        "Describe the visual design language used in each image.",
    ]

    for prompt in prompts:
        console.print(f"\n[bold]Analysis:[/bold] {prompt}")
        console.rule()
        run(image_urls=image_urls, prompt=prompt)
        console.print()


def demo_sequential_analysis():
    """Demo: Analyze images in sequence, building context."""
    console.print(Panel.fit(
        "[bold cyan]Sequential Image Analysis[/bold cyan]\n"
        "Analyzing images one by one with accumulated context",
        border_style="cyan"
    ))

    client = get_client()
    messages = []

    for i, url in enumerate(get_multi_images(), 1):
        console.print(f"\n[bold]Image {i}:[/bold]")

        messages.append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": url}},
                {"type": "text", "text": f"Describe image {i} briefly."}
            ]
        })

        response = client.create_chat(
            messages=messages,
            model=Models.VLM,
            thinking={"type": "disabled"}
        )

        content = response.choices[0].message.content
        messages.append({"role": "assistant", "content": content})

        console.print(Panel(Markdown(content), title=f"Description {i}", border_style="green"))

    # Final comparison using context
    messages.append({
        "role": "user",
        "content": "Now compare the two images you just described."
    })

    response = client.create_chat(
        messages=messages,
        model=Models.VLM,
        thinking={"type": "enabled"}
    )

    console.print(Panel(
        Markdown(response.choices[0].message.content),
        title="Comparison (with context)",
        border_style="cyan"
    ))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Image Analysis Example")
    parser.add_argument("-u", "--urls", nargs="+", help="Image URLs to compare")
    parser.add_argument("-p", "--prompt", type=str, help="Custom prompt")
    parser.add_argument("--demo-comparison", action="store_true",
                        help="Run product comparison demo")
    parser.add_argument("--demo-sequential", action="store_true",
                        help="Run sequential analysis demo")

    args = parser.parse_args()

    if args.demo_comparison:
        demo_product_comparison()
    elif args.demo_sequential:
        demo_sequential_analysis()
    else:
        run(image_urls=args.urls, prompt=args.prompt)
