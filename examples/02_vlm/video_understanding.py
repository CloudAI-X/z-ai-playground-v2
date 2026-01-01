"""
Video Understanding Example
Demonstrates GLM-4.6V's ability to analyze video content.
GLM-4.6V supports up to 128K context, enabling long video analysis.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel

from config import Models
from utils.client import get_client, print_error

console = Console()

# Sample video URL (public video for demo)
SAMPLE_VIDEO_URL = "https://cloud.video.taobao.com/play/u/null/p/1/e/6/t/1/d/ud/50782830612.mp4"


def run(video_url: str = None, prompt: str = None):
    """
    Analyze a video using GLM-4.6V.

    Args:
        video_url: URL of the video to analyze
        prompt: Question/instruction about the video
    """
    console.print(Panel.fit(
        "[bold cyan]Video Understanding Example[/bold cyan]\n"
        f"Model: {Models.VLM}\n"
        "Analyzing video content with 128K context window",
        border_style="cyan"
    ))

    video_url = video_url or SAMPLE_VIDEO_URL
    prompt = prompt or "Describe what is happening in this video. Include details about the scene, actions, and any notable elements."

    console.print(f"\n[bold]Video URL:[/bold] {video_url[:80]}...")
    console.print(f"[bold]Prompt:[/bold] {prompt}\n")

    try:
        client = get_client()

        # Construct multimodal message with video
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "video_url",
                    "video_url": {"url": video_url}
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]

        console.print("[dim]Analyzing video (this may take a moment)...[/dim]\n")

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
                    console.print(delta.content, end="")

        console.print("\n")

        if reasoning:
            console.print(Panel(
                reasoning[:500] + "..." if len(reasoning) > 500 else reasoning,
                title="Model Reasoning",
                border_style="blue"
            ))

        return {"content": content, "reasoning": reasoning}

    except Exception as e:
        print_error(e, "Video analysis failed")
        console.print(
            "\n[yellow]Note: Video analysis requires a valid, accessible video URL.[/yellow]\n"
            "[dim]The video must be publicly accessible and in a supported format.[/dim]"
        )
        return None


def demo_video_questions():
    """Demo: Ask different questions about a video."""
    console.print(Panel.fit(
        "[bold cyan]Video Q&A Demo[/bold cyan]\n"
        "Asking multiple questions about the same video",
        border_style="cyan"
    ))

    questions = [
        "Summarize this video in one sentence.",
        "What actions are being performed in this video?",
        "Describe the visual style and mood of this video.",
        "If this video had a title, what would it be?",
    ]

    client = get_client()

    for i, question in enumerate(questions, 1):
        console.print(f"\n[bold]Question {i}:[/bold] {question}")
        console.rule()

        try:
            messages = [{
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": SAMPLE_VIDEO_URL}},
                    {"type": "text", "text": question}
                ]
            }]

            response = client.create_chat(
                messages=messages,
                model=Models.VLM,
                thinking={"type": "disabled"}  # Faster for simple questions
            )

            console.print(Panel(
                response.choices[0].message.content,
                title="Answer",
                border_style="green"
            ))

        except Exception as e:
            print_error(e, f"Question {i} failed")


def demo_temporal_analysis():
    """Demo: Analyze temporal aspects of a video."""
    console.print(Panel.fit(
        "[bold cyan]Temporal Video Analysis[/bold cyan]\n"
        "Understanding sequence of events in video",
        border_style="cyan"
    ))

    prompt = """Analyze this video focusing on the temporal sequence:
    1. What happens at the beginning?
    2. What is the main action in the middle?
    3. How does the video end?
    4. Are there any transitions or changes in scene?

    Provide timestamps if you can estimate them."""

    run(prompt=prompt)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Video Understanding Example")
    parser.add_argument("-u", "--url", type=str, help="Video URL to analyze")
    parser.add_argument("-p", "--prompt", type=str, help="Custom prompt")
    parser.add_argument("--demo-qa", action="store_true",
                        help="Run video Q&A demo")
    parser.add_argument("--demo-temporal", action="store_true",
                        help="Run temporal analysis demo")

    args = parser.parse_args()

    if args.demo_qa:
        demo_video_questions()
    elif args.demo_temporal:
        demo_temporal_analysis()
    else:
        run(video_url=args.url, prompt=args.prompt)
