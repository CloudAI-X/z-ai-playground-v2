"""
Streaming Audio Transcription Example
Demonstrates real-time audio transcription with GLM-ASR-2512.
Returns results progressively as audio is processed.
"""

import sys
import json
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from config import Models, API_KEY, ENDPOINTS
from utils.client import print_error

console = Console()


def run(audio_path: str, language: str = None):
    """
    Stream transcription of an audio file using GLM-ASR-2512.

    Args:
        audio_path: Path to the audio file
        language: Optional language hint
    """
    console.print(Panel.fit(
        "[bold cyan]Streaming Audio Transcription[/bold cyan]\n"
        f"Model: {Models.AUDIO_ASR}\n"
        "Real-time progressive transcription",
        border_style="cyan"
    ))

    # Validate file
    audio_file = Path(audio_path)
    if not audio_file.exists():
        console.print(f"[red]Error: File not found: {audio_path}[/red]")
        return None

    file_size = audio_file.stat().st_size / (1024 * 1024)
    if file_size > 25:
        console.print(f"[red]Error: File too large ({file_size:.1f}MB). Maximum is 25MB.[/red]")
        return None

    console.print(f"\n[bold]Audio File:[/bold] {audio_path}")
    console.print(f"[bold]File Size:[/bold] {file_size:.2f} MB")
    console.print(f"[bold]Mode:[/bold] Streaming\n")

    try:
        console.print("[dim]Starting streaming transcription...[/dim]\n")

        url = ENDPOINTS["audio_transcription"]

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        files = {
            "file": (audio_file.name, open(audio_path, "rb"), "audio/mpeg")
        }

        data = {
            "model": Models.AUDIO_ASR,
            "stream": "true"  # Enable streaming
        }

        if language:
            data["language"] = language

        # Stream the response
        response = requests.post(url, headers=headers, files=files, data=data, stream=True)
        response.raise_for_status()

        full_text = ""
        segments = []

        console.print("[bold]Transcription:[/bold]")

        with Live(Text(""), console=console, refresh_per_second=10) as live:
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")

                    # Handle SSE format
                    if line_str.startswith("data:"):
                        data_str = line_str[5:].strip()

                        if data_str == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data_str)

                            if "text" in chunk:
                                full_text = chunk["text"]
                                live.update(Text(full_text, style="green"))

                            if "segment" in chunk:
                                segments.append(chunk["segment"])

                        except json.JSONDecodeError:
                            # Not JSON, might be partial text
                            pass

        console.print()  # New line after live display

        # Final result
        console.print(Panel(
            full_text or "No transcription received",
            title="Complete Transcription",
            border_style="green"
        ))

        if segments:
            console.print(f"\n[dim]Received {len(segments)} segments[/dim]")

        return {
            "text": full_text,
            "segments": segments
        }

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e.response.status_code}[/red]")
        console.print(f"[dim]{e.response.text}[/dim]")
        return None
    except Exception as e:
        print_error(e, "Streaming transcription failed")
        return None


def compare_streaming_vs_batch(audio_path: str):
    """
    Compare streaming vs batch transcription modes.

    Args:
        audio_path: Path to the audio file
    """
    console.print(Panel.fit(
        "[bold cyan]Streaming vs Batch Comparison[/bold cyan]\n"
        "Compare transcription modes",
        border_style="cyan"
    ))

    audio_file = Path(audio_path)
    if not audio_file.exists():
        console.print(f"[red]Error: File not found: {audio_path}[/red]")
        return None

    import time

    # Batch mode
    console.print("\n[bold]1. Batch Mode:[/bold]")
    console.print("[dim]Waiting for complete transcription...[/dim]")

    start_batch = time.time()

    url = ENDPOINTS["audio_transcription"]
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"file": (audio_file.name, open(audio_path, "rb"), "audio/mpeg")}
    data = {"model": Models.AUDIO_ASR, "stream": "false"}

    response = requests.post(url, headers=headers, files=files, data=data)
    batch_time = time.time() - start_batch

    if response.ok:
        batch_result = response.json()
        console.print(Panel(
            batch_result.get("text", "")[:200] + "...",
            title=f"Batch Result ({batch_time:.2f}s)",
            border_style="blue"
        ))
    else:
        console.print(f"[red]Batch failed: {response.status_code}[/red]")

    # Streaming mode
    console.print("\n[bold]2. Streaming Mode:[/bold]")
    console.print("[dim]Progressive transcription...[/dim]")

    start_stream = time.time()
    stream_result = run(audio_path)
    stream_time = time.time() - start_stream

    # Comparison
    console.print("\n[bold]Comparison:[/bold]")
    console.print(f"  Batch mode: {batch_time:.2f}s (complete result at end)")
    console.print(f"  Streaming: {stream_time:.2f}s (progressive updates)")

    return {
        "batch_time": batch_time,
        "stream_time": stream_time
    }


def demo_realtime_display():
    """
    Demo showing how streaming enables real-time UI updates.
    """
    console.print(Panel.fit(
        "[bold cyan]Real-time Display Demo[/bold cyan]\n"
        "Simulating live transcription display",
        border_style="cyan"
    ))

    console.print("""
[yellow]How streaming transcription works:[/yellow]

1. Audio file is uploaded to the API
2. Server begins processing immediately
3. Partial results are sent as they become available
4. Client displays text progressively

[bold]Benefits:[/bold]
- Users see results immediately
- Better UX for longer audio files
- Can show progress during processing
- Lower perceived latency

[bold]Use cases:[/bold]
- Live captioning applications
- Real-time meeting transcription
- Interactive voice assistants
- Accessibility features
""")

    console.print("\n[dim]To see streaming in action, run:[/dim]")
    console.print("[dim]python streaming_transcription.py -f your_audio.mp3[/dim]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Streaming Audio Transcription")
    parser.add_argument("-f", "--file", type=str, help="Path to audio file")
    parser.add_argument("-l", "--language", type=str,
                        help="Language hint (zh, en, ja, ko, de, fr)")
    parser.add_argument("--compare", action="store_true",
                        help="Compare streaming vs batch modes")
    parser.add_argument("--demo", action="store_true",
                        help="Show real-time display demo")

    args = parser.parse_args()

    if args.demo:
        demo_realtime_display()
    elif args.file:
        if args.compare:
            compare_streaming_vs_batch(args.file)
        else:
            run(args.file, language=args.language)
    else:
        console.print("[yellow]Please provide an audio file with -f/--file[/yellow]")
        console.print("[dim]Example: python streaming_transcription.py -f sample.mp3[/dim]")
        console.print("\n[dim]Or run --demo to see how streaming works[/dim]")
