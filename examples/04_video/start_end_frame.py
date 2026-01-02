"""
Start/End Frame Video Generation Example
Demonstrates CogVideoX-3's ability to generate videos with specified first and last frames.
Creates seamless transitions between two images.
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

from config import Models, SAMPLE_VIDEO_FRAMES
from utils.client import get_client, print_error

console = Console()


def run(
    start_image_url: str = None,
    end_image_url: str = None,
    prompt: str = None,
    quality: str = "quality",
    size: str = "1920x1080",
    fps: int = 30,
    with_audio: bool = True,
    poll_interval: int = 10,
    max_wait: int = 300
):
    """
    Generate a video with specified start and end frames using CogVideoX-3.

    Args:
        start_image_url: URL of the first frame image
        end_image_url: URL of the last frame image
        prompt: Optional text prompt to guide the transition
        quality: "quality" for higher quality, "speed" for faster generation
        size: Video dimensions
        fps: Frames per second (30 or 60)
        with_audio: Whether to include generated audio
        poll_interval: Seconds between status checks
        max_wait: Maximum seconds to wait for completion
    """
    console.print(Panel.fit(
        "[bold cyan]Start/End Frame Video Generation[/bold cyan]\n"
        f"Model: {Models.VIDEO_GEN}\n"
        "Create seamless transitions between two images",
        border_style="cyan"
    ))

    # Use sample frame URLs if not provided (video gen requires HTTP URLs)
    start_image_url = start_image_url or SAMPLE_VIDEO_FRAMES["first"]
    end_image_url = end_image_url or SAMPLE_VIDEO_FRAMES["last"]
    prompt = prompt or "Smooth transition between the two frames with natural motion"

    console.print(f"\n[bold]Start Frame:[/bold] {start_image_url[:50]}...")
    console.print(f"[bold]End Frame:[/bold] {end_image_url[:50]}...")
    console.print(f"[bold]Transition Prompt:[/bold] {prompt}")
    console.print(f"[bold]Quality:[/bold] {quality}")
    console.print(f"[bold]Size:[/bold] {size}\n")

    try:
        client = get_client()

        console.print("[dim]Submitting start/end frame video request...[/dim]\n")

        # Submit the video generation job with start and end frames
        # Using image_url as a list [start_frame, end_frame]
        response = client.generate_video(
            prompt=prompt,
            image_url=[start_image_url, end_image_url],
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
            task = progress.add_task("Creating transition video...", total=None)

            elapsed = 0
            while elapsed < max_wait:
                result = client.retrieve_video_result(video_id)

                if result.task_status == "SUCCESS":
                    progress.stop()
                    video_url = result.video_result[0].url if result.video_result else None
                    cover_url = result.video_result[0].cover_image_url if result.video_result else None

                    console.print(Panel(
                        "[green]Transition video generated![/green]",
                        title="Result",
                        border_style="green"
                    ))

                    # Print URLs outside panel to avoid line wrapping (makes them clickable)
                    console.print(f"\n[bold]Video URL:[/bold]")
                    console.print(video_url, soft_wrap=True, overflow="ignore")
                    console.print(f"\n[bold]Cover Image:[/bold]")
                    console.print(cover_url, soft_wrap=True, overflow="ignore")

                    return {
                        "id": video_id,
                        "video_url": video_url,
                        "cover_url": cover_url,
                        "start_frame": start_image_url,
                        "end_frame": end_image_url,
                        "prompt": prompt
                    }

                elif result.task_status == "FAIL":
                    progress.stop()
                    console.print(f"[red]Video generation failed![/red]")
                    return None

                progress.update(task, description=f"Creating transition... ({elapsed}s elapsed)")
                time.sleep(poll_interval)
                elapsed += poll_interval

            console.print("[yellow]Timeout waiting for video generation[/yellow]")
            console.print(f"[dim]Check status later with ID: {video_id}[/dim]")
            return {"id": video_id, "status": "pending"}

    except Exception as e:
        print_error(e, "Start/end frame video generation failed")
        return None


def demo_transition_effects():
    """Demo: Different transition styles between same frames."""
    console.print(Panel.fit(
        "[bold cyan]Transition Effects Demo[/bold cyan]\n"
        "Same frames with different transition styles",
        border_style="cyan"
    ))

    start_url = SAMPLE_VIDEO_FRAMES["first"]
    end_url = SAMPLE_VIDEO_FRAMES["last"]

    transition_prompts = [
        "Smooth morph transition with flowing movement",
        "Dramatic zoom and pan transition",
        "Fade through motion blur effect",
    ]

    results = []
    for prompt in transition_prompts:
        console.print(f"\n[bold]Transition:[/bold] {prompt}")
        result = run(
            start_image_url=start_url,
            end_image_url=end_url,
            prompt=prompt,
            quality="speed",
            max_wait=180
        )
        if result:
            results.append(result)

    return results


def demo_story_sequence():
    """Demo: Create a story sequence with multiple frame pairs."""
    console.print(Panel.fit(
        "[bold cyan]Story Sequence Demo[/bold cyan]\n"
        "Creating narrative flow between frames",
        border_style="cyan"
    ))

    console.print("[dim]Using sample frame URLs...[/dim]\n")

    # Create a circular story: frame1 -> frame2 -> frame1
    sequences = [
        (SAMPLE_VIDEO_FRAMES["first"], SAMPLE_VIDEO_FRAMES["last"], "Scene transition with natural movement"),
        (SAMPLE_VIDEO_FRAMES["last"], SAMPLE_VIDEO_FRAMES["first"], "Return to the beginning, completing the cycle"),
    ]

    results = []
    for i, (start, end, prompt) in enumerate(sequences, 1):
        console.print(f"\n[bold]Sequence {i}:[/bold] {prompt}")
        result = run(
            start_image_url=start,
            end_image_url=end,
            prompt=prompt,
            quality="speed",
            max_wait=180
        )
        if result:
            results.append(result)

    console.print("\n[green]Story sequence complete![/green]")
    console.print("[dim]Combine these videos for a seamless loop.[/dim]")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Start/End Frame Video Generation")
    parser.add_argument("--start", type=str, help="Start frame image URL")
    parser.add_argument("--end", type=str, help="End frame image URL")
    parser.add_argument("-p", "--prompt", type=str,
                        help="Transition prompt to guide the animation")
    parser.add_argument("-q", "--quality", type=str, default="quality",
                        choices=["quality", "speed"], help="Quality mode")
    parser.add_argument("-s", "--size", type=str, default="1920x1080",
                        help="Video size")
    parser.add_argument("--fps", type=int, default=30, choices=[30, 60],
                        help="Frames per second")
    parser.add_argument("--demo-transitions", action="store_true",
                        help="Run transition effects demo")
    parser.add_argument("--demo-story", action="store_true",
                        help="Run story sequence demo")

    args = parser.parse_args()

    if args.demo_transitions:
        demo_transition_effects()
    elif args.demo_story:
        demo_story_sequence()
    else:
        run(
            start_image_url=args.start,
            end_image_url=args.end,
            prompt=args.prompt,
            quality=args.quality,
            size=args.size,
            fps=args.fps
        )
