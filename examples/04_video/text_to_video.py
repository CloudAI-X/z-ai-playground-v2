"""
Text-to-Video Generation Example
Demonstrates CogVideoX-3's ability to generate videos from text prompts.
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

from config import Models, TEST_PROMPTS
from utils.client import get_client, print_error

console = Console()


def run(
    prompt: str = None,
    quality: str = "quality",
    size: str = "1920x1080",
    fps: int = 30,
    with_audio: bool = True,
    poll_interval: int = 10,
    max_wait: int = 300
):
    """
    Generate a video from a text prompt using CogVideoX-3.

    Args:
        prompt: Text description of the video to generate
        quality: "quality" for higher quality, "speed" for faster generation
        size: Video dimensions (up to 4K supported)
        fps: Frames per second (30 or 60)
        with_audio: Whether to include generated audio
        poll_interval: Seconds between status checks
        max_wait: Maximum seconds to wait for completion
    """
    console.print(Panel.fit(
        "[bold cyan]Text-to-Video Generation[/bold cyan]\n"
        f"Model: {Models.VIDEO_GEN}\n"
        "Generate videos from text descriptions",
        border_style="cyan"
    ))

    prompt = prompt or TEST_PROMPTS["video_gen"]

    console.print(f"\n[bold]Prompt:[/bold] {prompt}")
    console.print(f"[bold]Quality:[/bold] {quality}")
    console.print(f"[bold]Size:[/bold] {size}")
    console.print(f"[bold]FPS:[/bold] {fps}")
    console.print(f"[bold]Audio:[/bold] {'Yes' if with_audio else 'No'}\n")

    try:
        client = get_client()

        console.print("[dim]Submitting video generation request...[/dim]\n")

        # Submit the video generation job
        response = client.generate_video(
            prompt=prompt,
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
            task = progress.add_task("Waiting for video generation...", total=None)

            elapsed = 0
            while elapsed < max_wait:
                result = client.retrieve_video_result(video_id)

                if result.task_status == "SUCCESS":
                    progress.stop()
                    video_url = result.video_result[0].url if result.video_result else None
                    cover_url = result.video_result[0].cover_image_url if result.video_result else None

                    console.print(Panel(
                        "[green]Video generated successfully![/green]",
                        title="Result",
                        border_style="green"
                    ))

                    # Print URLs outside panel to avoid line wrapping (makes them clickable)
                    console.print(f"\n[bold]Video URL:[/bold]")
                    console.print(video_url, soft_wrap=True, overflow="ignore")
                    console.print(f"\n[bold]Cover Image:[/bold]")
                    console.print(cover_url, soft_wrap=True, overflow="ignore")

                    console.print(
                        "\n[dim]Note: URLs are temporary. Download the video to save it.[/dim]"
                    )

                    return {
                        "id": video_id,
                        "video_url": video_url,
                        "cover_url": cover_url,
                        "prompt": prompt
                    }

                elif result.task_status == "FAIL":
                    progress.stop()
                    console.print(f"[red]Video generation failed![/red]")
                    return None

                progress.update(task, description=f"Generating video... ({elapsed}s elapsed)")
                time.sleep(poll_interval)
                elapsed += poll_interval

            console.print("[yellow]Timeout waiting for video generation[/yellow]")
            console.print(f"[dim]Check status later with ID: {video_id}[/dim]")
            return {"id": video_id, "status": "pending"}

    except Exception as e:
        print_error(e, "Video generation failed")
        return None


def demo_quality_comparison():
    """Demo: Compare quality vs speed modes."""
    console.print(Panel.fit(
        "[bold cyan]Quality vs Speed Comparison[/bold cyan]\n"
        "Generating same prompt with different quality settings",
        border_style="cyan"
    ))

    prompt = "A colorful butterfly gracefully landing on a purple flower"

    modes = [
        ("speed", "Fast generation (lower quality)"),
        ("quality", "High quality (slower)"),
    ]

    results = []
    for mode, description in modes:
        console.print(f"\n[bold]{description}:[/bold]")
        result = run(prompt=prompt, quality=mode, max_wait=180)
        if result:
            results.append(result)

    return results


def demo_various_sizes():
    """Demo: Generate videos in different resolutions."""
    console.print(Panel.fit(
        "[bold cyan]Video Resolution Demo[/bold cyan]\n"
        "Generating videos in various sizes",
        border_style="cyan"
    ))

    sizes = [
        ("1280x720", "720p HD"),
        ("1920x1080", "1080p Full HD"),
        ("2560x1440", "1440p 2K"),
    ]

    prompt = "Ocean waves gently rolling onto a sandy beach at sunset"

    results = []
    for size, description in sizes:
        console.print(f"\n[bold]{description} ({size}):[/bold]")
        result = run(prompt=prompt, size=size, quality="speed", max_wait=180)
        if result:
            results.append(result)

    return results


def check_status(video_id: str):
    """
    Check the status of a video generation job.

    Args:
        video_id: The ID returned from a video generation request
    """
    console.print(f"\n[bold]Checking status for:[/bold] {video_id}\n")

    try:
        client = get_client()
        result = client.retrieve_video_result(video_id)

        if result.task_status == "SUCCESS":
            video_url = result.video_result[0].url if result.video_result else None
            console.print(Panel(
                "[green]Status: SUCCESS[/green]",
                border_style="green"
            ))
            console.print(f"\n[bold]Video URL:[/bold]")
            console.print(video_url, soft_wrap=True, overflow="ignore")
        elif result.task_status == "FAIL":
            console.print("[red]Status: FAILED[/red]")
        else:
            console.print(f"[yellow]Status: {result.task_status}[/yellow]")

        return result

    except Exception as e:
        print_error(e, "Status check failed")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Text-to-Video Generation")
    parser.add_argument("-p", "--prompt", type=str, help="Video generation prompt")
    parser.add_argument("-q", "--quality", type=str, default="quality",
                        choices=["quality", "speed"], help="Quality mode")
    parser.add_argument("-s", "--size", type=str, default="1920x1080",
                        help="Video size (e.g., 1920x1080)")
    parser.add_argument("--fps", type=int, default=30, choices=[30, 60],
                        help="Frames per second")
    parser.add_argument("--no-audio", action="store_true",
                        help="Disable audio generation")
    parser.add_argument("--check", type=str, metavar="ID",
                        help="Check status of a video generation job")
    parser.add_argument("--demo-quality", action="store_true",
                        help="Run quality comparison demo")
    parser.add_argument("--demo-sizes", action="store_true",
                        help="Run resolution demo")

    args = parser.parse_args()

    if args.check:
        check_status(args.check)
    elif args.demo_quality:
        demo_quality_comparison()
    elif args.demo_sizes:
        demo_various_sizes()
    else:
        run(
            prompt=args.prompt,
            quality=args.quality,
            size=args.size,
            fps=args.fps,
            with_audio=not args.no_audio
        )
