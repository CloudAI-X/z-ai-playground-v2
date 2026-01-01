"""
Image-to-Video Generation Example
Demonstrates CogVideoX-3's ability to animate static images.
Cost: $0.2 per video
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import Models, SAMPLE_IMAGES
from utils.client import get_client, print_error

console = Console()


def run(
    image_url: str = None,
    prompt: str = None,
    quality: str = "quality",
    size: str = "1920x1080",
    fps: int = 30,
    with_audio: bool = True,
    poll_interval: int = 10,
    max_wait: int = 300
):
    """
    Generate a video from a source image using CogVideoX-3.

    Args:
        image_url: URL of the source image to animate
        prompt: Optional text prompt to guide the animation
        quality: "quality" for higher quality, "speed" for faster generation
        size: Video dimensions
        fps: Frames per second (30 or 60)
        with_audio: Whether to include generated audio
        poll_interval: Seconds between status checks
        max_wait: Maximum seconds to wait for completion
    """
    console.print(Panel.fit(
        "[bold cyan]Image-to-Video Generation[/bold cyan]\n"
        f"Model: {Models.VIDEO_GEN}\n"
        "Animate static images into videos",
        border_style="cyan"
    ))

    image_url = image_url or SAMPLE_IMAGES[0]
    prompt = prompt or "Animate this image with natural, smooth motion"

    console.print(f"\n[bold]Source Image:[/bold] {image_url[:60]}...")
    console.print(f"[bold]Animation Prompt:[/bold] {prompt}")
    console.print(f"[bold]Quality:[/bold] {quality}")
    console.print(f"[bold]Size:[/bold] {size}\n")

    try:
        client = get_client()

        console.print("[dim]Submitting image-to-video request...[/dim]\n")

        # Submit the video generation job with image
        response = client.generate_video(
            prompt=prompt,
            image_url=image_url,
            quality=quality,
            size=size,
            fps=fps,
            with_audio=with_audio
        )

        video_id = response.id
        console.print(f"[green]Job submitted![/green] ID: {video_id}\n")

        # Poll for completion
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Animating image...", total=None)

            elapsed = 0
            while elapsed < max_wait:
                result = client.retrieve_video_result(video_id)

                if result.task_status == "SUCCESS":
                    progress.stop()
                    video_url = result.video_result[0].url if result.video_result else None
                    cover_url = result.video_result[0].cover_image_url if result.video_result else None

                    console.print(Panel(
                        f"[green]Video generated successfully![/green]\n\n"
                        f"[bold]Video URL:[/bold]\n{video_url}\n\n"
                        f"[bold]Cover Image:[/bold]\n{cover_url}",
                        title="Result",
                        border_style="green"
                    ))

                    return {
                        "id": video_id,
                        "video_url": video_url,
                        "cover_url": cover_url,
                        "source_image": image_url,
                        "prompt": prompt
                    }

                elif result.task_status == "FAIL":
                    progress.stop()
                    console.print(f"[red]Video generation failed![/red]")
                    return None

                progress.update(task, description=f"Animating image... ({elapsed}s elapsed)")
                time.sleep(poll_interval)
                elapsed += poll_interval

            console.print("[yellow]Timeout waiting for video generation[/yellow]")
            console.print(f"[dim]Check status later with ID: {video_id}[/dim]")
            return {"id": video_id, "status": "pending"}

    except Exception as e:
        print_error(e, "Image-to-video generation failed")
        return None


def demo_animation_styles():
    """Demo: Different animation styles for the same image."""
    console.print(Panel.fit(
        "[bold cyan]Animation Styles Demo[/bold cyan]\n"
        "Animating the same image with different prompts",
        border_style="cyan"
    ))

    image_url = SAMPLE_IMAGES[0]

    animation_prompts = [
        "Gentle zoom in with subtle motion",
        "Dramatic camera pan from left to right",
        "Add flowing water and wind movement",
        "Create a time-lapse effect with changing light",
    ]

    results = []
    for prompt in animation_prompts:
        console.print(f"\n[bold]Animation:[/bold] {prompt}")
        result = run(
            image_url=image_url,
            prompt=prompt,
            quality="speed",
            max_wait=180
        )
        if result:
            results.append(result)

    return results


def demo_with_multiple_images():
    """Demo: Animate different source images."""
    console.print(Panel.fit(
        "[bold cyan]Multiple Image Animation Demo[/bold cyan]\n"
        "Animating different source images",
        border_style="cyan"
    ))

    results = []
    for i, image_url in enumerate(SAMPLE_IMAGES[:2], 1):
        console.print(f"\n[bold]Image {i}:[/bold]")
        result = run(
            image_url=image_url,
            prompt="Bring this image to life with natural movement",
            quality="speed",
            max_wait=180
        )
        if result:
            results.append(result)

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image-to-Video Generation")
    parser.add_argument("-i", "--image", type=str, help="Source image URL")
    parser.add_argument("-p", "--prompt", type=str,
                        help="Animation prompt to guide motion")
    parser.add_argument("-q", "--quality", type=str, default="quality",
                        choices=["quality", "speed"], help="Quality mode")
    parser.add_argument("-s", "--size", type=str, default="1920x1080",
                        help="Video size")
    parser.add_argument("--fps", type=int, default=30, choices=[30, 60],
                        help="Frames per second")
    parser.add_argument("--demo-styles", action="store_true",
                        help="Run animation styles demo")
    parser.add_argument("--demo-images", action="store_true",
                        help="Run multiple images demo")

    args = parser.parse_args()

    if args.demo_styles:
        demo_animation_styles()
    elif args.demo_images:
        demo_with_multiple_images()
    else:
        run(
            image_url=args.image,
            prompt=args.prompt,
            quality=args.quality,
            size=args.size,
            fps=args.fps
        )
