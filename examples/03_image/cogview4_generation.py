"""
CogView-4 Image Generation Example
Demonstrates text-to-image generation with various sizes and styles.
Cost: $0.01 per image
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Models, TEST_PROMPTS
from utils.client import get_client, print_error

console = Console()


def run(prompt: str = None, size: str = "1024x1024"):
    """
    Generate an image using CogView-4.

    Args:
        prompt: Text description of the image to generate
        size: Image dimensions (e.g., "1024x1024", "1920x1080", "768x1344")
    """
    console.print(Panel.fit(
        "[bold cyan]CogView-4 Image Generation[/bold cyan]\n"
        f"Model: {Models.IMAGE_GEN}\n"
        "Text-to-image with flexible sizes",
        border_style="cyan"
    ))

    prompt = prompt or TEST_PROMPTS["image_gen"]

    console.print(f"\n[bold]Prompt:[/bold] {prompt}")
    console.print(f"[bold]Size:[/bold] {size}\n")

    try:
        client = get_client()

        console.print("[dim]Generating image...[/dim]\n")

        response = client.generate_image(
            prompt=prompt,
            size=size
        )

        if response.data:
            image_url = response.data[0].url
            console.print(Panel(
                "[green]Image generated successfully![/green]",
                title="Result",
                border_style="green"
            ))

            # Print URL outside panel to avoid line wrapping (makes it clickable)
            console.print(f"\n[bold]URL:[/bold]")
            console.print(image_url, soft_wrap=True, overflow="ignore")

            console.print(
                "\n[dim]Note: The URL is temporary. Download the image to save it.[/dim]"
            )

            return {"url": image_url, "prompt": prompt, "size": size}
        else:
            console.print("[yellow]No image data returned[/yellow]")
            return None

    except Exception as e:
        print_error(e, "Image generation failed")
        return None


def demo_multiple_sizes():
    """Demo: Generate images in various sizes."""
    console.print(Panel.fit(
        "[bold cyan]Multi-Size Generation Demo[/bold cyan]\n"
        "Generating the same prompt in different sizes",
        border_style="cyan"
    ))

    sizes = [
        ("1024x1024", "Square (1:1)"),
        ("1344x768", "Landscape (16:9)"),
        ("768x1344", "Portrait (9:16)"),
        ("1920x1080", "Full HD Landscape"),
    ]

    prompt = "A peaceful zen garden with raked sand patterns and moss-covered stones"

    results = []
    for size, description in sizes:
        console.print(f"\n[bold]Generating {description}:[/bold] {size}")
        result = run(prompt=prompt, size=size)
        if result:
            results.append(result)

    # Summary table
    if results:
        console.print("\n")
        table = Table(title="Generation Results")
        table.add_column("Size", style="cyan")
        table.add_column("URL (truncated)", style="green")

        for result in results:
            table.add_row(result["size"], result["url"][:60] + "...")

        console.print(table)

    return results


def demo_style_variations():
    """Demo: Generate images with different artistic styles."""
    console.print(Panel.fit(
        "[bold cyan]Style Variations Demo[/bold cyan]\n"
        "Same subject with different artistic styles",
        border_style="cyan"
    ))

    base_subject = "a majestic lion"

    style_prompts = [
        ("Photorealistic", f"Photorealistic {base_subject} in golden savanna light, "
                          "wildlife photography, sharp focus, natural lighting"),
        ("Oil Painting", f"Oil painting of {base_subject}, impressionist style, "
                        "bold brush strokes, rich colors, canvas texture"),
        ("Anime Style", f"Anime illustration of {base_subject}, Studio Ghibli style, "
                       "vibrant colors, detailed fur, fantasy elements"),
        ("Watercolor", f"Delicate watercolor painting of {base_subject}, "
                      "soft edges, flowing colors, artistic splashes"),
    ]

    results = []
    for style_name, prompt in style_prompts:
        console.print(f"\n[bold]{style_name}:[/bold]")
        console.print(f"[dim]{prompt[:80]}...[/dim]")
        result = run(prompt=prompt, size="1024x1024")
        if result:
            result["style"] = style_name
            results.append(result)

    return results


def demo_chinese_prompt():
    """Demo: Generate images with Chinese language prompts."""
    console.print(Panel.fit(
        "[bold cyan]Chinese Prompt Demo[/bold cyan]\n"
        "CogView-4 supports both Chinese and English",
        border_style="cyan"
    ))

    chinese_prompts = [
        "一只可爱的橘猫坐在窗台上，望着窗外的雪景，温馨的室内氛围",
        "水墨画风格的山水画，远山近水，一叶扁舟",
        "春天的樱花树下，一位穿着汉服的少女撑着油纸伞",
    ]

    results = []
    for prompt in chinese_prompts:
        console.print(f"\n[bold]Prompt:[/bold] {prompt}")
        result = run(prompt=prompt, size="1024x1024")
        if result:
            results.append(result)

    return results


def generate_batch(prompts: list, size: str = "1024x1024"):
    """
    Generate multiple images from a list of prompts.

    Args:
        prompts: List of text prompts
        size: Image size for all generations
    """
    console.print(Panel.fit(
        "[bold cyan]Batch Image Generation[/bold cyan]\n"
        f"Generating {len(prompts)} images",
        border_style="cyan"
    ))

    results = []
    for i, prompt in enumerate(prompts, 1):
        console.print(f"\n[bold]Image {i}/{len(prompts)}:[/bold]")
        result = run(prompt=prompt, size=size)
        if result:
            results.append(result)

    console.print(f"\n[green]Successfully generated {len(results)}/{len(prompts)} images[/green]")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CogView-4 Image Generation")
    parser.add_argument("-p", "--prompt", type=str, help="Image generation prompt")
    parser.add_argument("-s", "--size", type=str, default="1024x1024",
                        help="Image size (e.g., 1024x1024)")
    parser.add_argument("--demo-sizes", action="store_true",
                        help="Run multi-size demo")
    parser.add_argument("--demo-styles", action="store_true",
                        help="Run style variations demo")
    parser.add_argument("--demo-chinese", action="store_true",
                        help="Run Chinese prompts demo")

    args = parser.parse_args()

    if args.demo_sizes:
        demo_multiple_sizes()
    elif args.demo_styles:
        demo_style_variations()
    elif args.demo_chinese:
        demo_chinese_prompt()
    else:
        run(prompt=args.prompt, size=args.size)
