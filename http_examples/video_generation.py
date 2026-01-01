"""
HTTP Video Generation Example
Demonstrates direct HTTP API calls for CogVideoX-3 video generation.
This is an async operation: submit job, then poll for result.
"""

import sys
import json
import time
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import API_KEY, ENDPOINTS, Models, TEST_PROMPTS

console = Console()

# HTTP request timeouts in seconds
HTTP_TIMEOUT = 60  # For non-streaming requests


def run(
    prompt: str = None,
    quality: str = "quality",
    size: str = "1920x1080",
    poll_interval: int = 10,
    max_wait: int = 300
):
    """
    Make direct HTTP API calls for video generation.

    Args:
        prompt: Video description
        quality: "quality" or "speed"
        size: Video dimensions
        poll_interval: Seconds between status checks
        max_wait: Maximum seconds to wait
    """
    console.print(Panel.fit(
        "[bold cyan]HTTP Video Generation[/bold cyan]\n"
        f"Model: {Models.VIDEO_GEN}\n"
        "Direct API calls without SDK (async pattern)",
        border_style="cyan"
    ))

    prompt = prompt or TEST_PROMPTS["video_gen"]

    console.print(f"\n[bold]Prompt:[/bold] {prompt}")
    console.print(f"[bold]Quality:[/bold] {quality}")
    console.print(f"[bold]Size:[/bold] {size}\n")

    # Step 1: Submit the video generation job
    url = ENDPOINTS["video_generation"]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": Models.VIDEO_GEN,
        "prompt": prompt,
        "quality": quality,
        "size": size,
        "fps": 30,
        "with_audio": True
    }

    # Show the request
    console.print("[bold]Step 1: Submit Job[/bold]")
    syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
    console.print(syntax)
    console.print()

    try:
        console.print("[dim]Submitting video generation request...[/dim]\n")

        response = requests.post(url, headers=headers, json=payload, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        result = response.json()

        # Get the job ID
        video_id = result.get("id")
        if not video_id:
            console.print("[red]No job ID in response[/red]")
            console.print(f"Response: {result}")
            return None

        console.print(f"[green]Job submitted![/green] ID: {video_id}")

        # Step 2: Poll for completion
        console.print("\n[bold]Step 2: Poll for Result[/bold]")

        status_url = f"{ENDPOINTS['video_result']}/{video_id}"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating video...", total=None)

            elapsed = 0
            while elapsed < max_wait:
                status_response = requests.get(status_url, headers=headers, timeout=HTTP_TIMEOUT)
                status_response.raise_for_status()

                status_result = status_response.json()
                task_status = status_result.get("task_status")

                if task_status == "SUCCESS":
                    progress.stop()

                    console.print("\n[bold]Response:[/bold]")
                    syntax = Syntax(json.dumps(status_result, indent=2), "json", theme="monokai")
                    console.print(syntax)

                    # Extract video URL
                    video_result = status_result.get("video_result", [])
                    if video_result:
                        video_url = video_result[0].get("url")
                        cover_url = video_result[0].get("cover_image_url")

                        console.print(Panel(
                            f"[green]Video generated successfully![/green]\n\n"
                            f"[bold]Video URL:[/bold]\n{video_url}\n\n"
                            f"[bold]Cover:[/bold]\n{cover_url}",
                            title="Result",
                            border_style="green"
                        ))

                    return status_result

                elif task_status == "FAIL":
                    progress.stop()
                    console.print("[red]Video generation failed![/red]")
                    console.print(f"Response: {status_result}")
                    return None

                progress.update(task, description=f"Status: {task_status} ({elapsed}s)")
                time.sleep(poll_interval)
                elapsed += poll_interval

            console.print(f"[yellow]Timeout after {max_wait}s[/yellow]")
            console.print(f"[dim]Check status later with ID: {video_id}[/dim]")
            return {"id": video_id, "status": "pending"}

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e.response.status_code}[/red]")
        console.print(f"[dim]{e.response.text}[/dim]")
        return None
    except requests.exceptions.Timeout as e:
        console.print(f"[red]Timeout Error: Request timed out[/red]")
        console.print(f"[dim]{e}[/dim]")
        return None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None


def check_status(video_id: str):
    """
    Check the status of a video generation job.

    Args:
        video_id: The job ID
    """
    console.print(Panel.fit(
        "[bold cyan]Check Video Status[/bold cyan]\n"
        "Query the status of a video job",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Job ID:[/bold] {video_id}\n")

    url = f"{ENDPOINTS['video_result']}/{video_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        result = response.json()

        console.print("[bold]Status Response:[/bold]")
        syntax = Syntax(json.dumps(result, indent=2), "json", theme="monokai")
        console.print(syntax)

        task_status = result.get("task_status")
        console.print(f"\n[bold]Status:[/bold] {task_status}")

        if task_status == "SUCCESS":
            video_result = result.get("video_result", [])
            if video_result:
                console.print(f"[green]Video URL:[/green] {video_result[0].get('url')}")

        return result

    except requests.exceptions.Timeout as e:
        console.print(f"[red]Timeout Error: Request timed out[/red]")
        console.print(f"[dim]{e}[/dim]")
        return None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None


def show_curl_examples():
    """Show equivalent curl commands for video generation."""
    console.print(Panel.fit(
        "[bold cyan]Curl Examples[/bold cyan]\n"
        "Video generation curl commands",
        border_style="cyan"
    ))

    examples = [
        {
            "name": "Step 1: Submit Video Job",
            "curl": f'''curl -X POST "{ENDPOINTS["video_generation"]}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.VIDEO_GEN}",
    "prompt": "A butterfly landing on a flower",
    "quality": "quality",
    "size": "1920x1080",
    "fps": 30,
    "with_audio": true
  }}'

# Response will contain an "id" field, e.g., "abc123"
'''
        },
        {
            "name": "Step 2: Poll for Result",
            "curl": f'''# Replace VIDEO_ID with the id from step 1
curl -X GET "{ENDPOINTS["video_result"]}/VIDEO_ID" \\
  -H "Authorization: Bearer $Z_AI_API_KEY"

# Repeat until task_status is "SUCCESS" or "FAIL"
'''
        },
        {
            "name": "Image-to-Video",
            "curl": f'''curl -X POST "{ENDPOINTS["video_generation"]}" \\
  -H "Authorization: Bearer $Z_AI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{Models.VIDEO_GEN}",
    "prompt": "Animate with gentle motion",
    "image_url": "https://example.com/image.png",
    "quality": "quality"
  }}'
'''
        }
    ]

    for example in examples:
        console.print(f"\n[bold]{example['name']}:[/bold]")
        syntax = Syntax(example["curl"], "bash", theme="monokai")
        console.print(syntax)


def show_async_pattern():
    """Explain the async video generation pattern."""
    console.print(Panel.fit(
        "[bold cyan]Async Pattern Explanation[/bold cyan]\n"
        "Understanding video generation workflow",
        border_style="cyan"
    ))

    console.print("""
[bold]Video Generation is Asynchronous[/bold]

Unlike chat or image generation, video generation takes longer
and uses an async pattern:

[cyan]1. Submit Job[/cyan]
   POST /videos/generations
   → Returns a job ID immediately

[cyan]2. Poll for Status[/cyan]
   GET /videos/{id}
   → Returns current status

[cyan]3. Status Values[/cyan]
   - PROCESSING: Still generating
   - SUCCESS: Video is ready
   - FAIL: Generation failed

[cyan]4. On SUCCESS[/cyan]
   - video_result[].url: Video download URL
   - video_result[].cover_image_url: Thumbnail

[yellow]Typical Timeline:[/yellow]
   - Quality mode: 1-5 minutes
   - Speed mode: 30-90 seconds

[yellow]Cost:[/yellow] $0.2 per video
""")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HTTP Video Generation Example")
    parser.add_argument("-p", "--prompt", type=str, help="Video prompt")
    parser.add_argument("-q", "--quality", type=str, default="quality",
                        choices=["quality", "speed"], help="Quality mode")
    parser.add_argument("-s", "--size", type=str, default="1920x1080",
                        help="Video size")
    parser.add_argument("--check", type=str, metavar="ID",
                        help="Check status of a job")
    parser.add_argument("--show-curl", action="store_true",
                        help="Show curl examples")
    parser.add_argument("--show-pattern", action="store_true",
                        help="Explain async pattern")

    args = parser.parse_args()

    if args.check:
        check_status(args.check)
    elif args.show_curl:
        show_curl_examples()
    elif args.show_pattern:
        show_async_pattern()
    else:
        run(prompt=args.prompt, quality=args.quality, size=args.size)
