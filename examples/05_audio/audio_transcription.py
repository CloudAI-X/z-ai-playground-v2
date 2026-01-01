"""
Audio Transcription Example
Demonstrates GLM-ASR-2512's ability to transcribe audio to text.
Constraints: ≤30 seconds audio, ≤25MB file size
Supported: Chinese, English, French, German, Japanese, Korean, etc.
"""

import sys
import os
import requests
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Models, API_KEY, ENDPOINTS
from utils.client import print_error

console = Console()


def run(audio_path: str, language: str = None):
    """
    Transcribe an audio file using GLM-ASR-2512.

    Args:
        audio_path: Path to the audio file (MP3, WAV, etc.)
        language: Optional language hint (e.g., "zh" for Chinese, "en" for English)
    """
    console.print(Panel.fit(
        "[bold cyan]Audio Transcription[/bold cyan]\n"
        f"Model: {Models.AUDIO_ASR}\n"
        "Convert speech to text",
        border_style="cyan"
    ))

    # Validate file
    audio_file = Path(audio_path)
    if not audio_file.exists():
        console.print(f"[red]Error: File not found: {audio_path}[/red]")
        return None

    file_size = audio_file.stat().st_size / (1024 * 1024)  # MB
    if file_size > 25:
        console.print(f"[red]Error: File too large ({file_size:.1f}MB). Maximum is 25MB.[/red]")
        return None

    console.print(f"\n[bold]Audio File:[/bold] {audio_path}")
    console.print(f"[bold]File Size:[/bold] {file_size:.2f} MB")
    if language:
        console.print(f"[bold]Language:[/bold] {language}")
    console.print()

    try:
        console.print("[dim]Transcribing audio...[/dim]\n")

        # Use HTTP API directly for audio transcription
        url = ENDPOINTS["audio_transcription"]

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        files = {
            "file": (audio_file.name, open(audio_path, "rb"), "audio/mpeg")
        }

        data = {
            "model": Models.AUDIO_ASR,
            "stream": "false"
        }

        if language:
            data["language"] = language

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()

        result = response.json()

        # Display the transcription
        if "text" in result:
            console.print(Panel(
                result["text"],
                title="Transcription",
                border_style="green"
            ))

            # Show additional metadata if available
            if "segments" in result:
                table = Table(title="Segments")
                table.add_column("Start", style="cyan")
                table.add_column("End", style="cyan")
                table.add_column("Text", style="white")

                for segment in result["segments"][:10]:  # Show first 10 segments
                    table.add_row(
                        f"{segment.get('start', 0):.2f}s",
                        f"{segment.get('end', 0):.2f}s",
                        segment.get("text", "")[:50]
                    )

                console.print(table)

            return result

        else:
            console.print(Panel(str(result), title="Response", border_style="yellow"))
            return result

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]HTTP Error: {e.response.status_code}[/red]")
        console.print(f"[dim]{e.response.text}[/dim]")
        return None
    except Exception as e:
        print_error(e, "Transcription failed")
        return None


def transcribe_with_timestamps(audio_path: str):
    """
    Transcribe audio and request detailed timestamps.

    Args:
        audio_path: Path to the audio file
    """
    console.print(Panel.fit(
        "[bold cyan]Transcription with Timestamps[/bold cyan]\n"
        "Get word-level or segment-level timing",
        border_style="cyan"
    ))

    audio_file = Path(audio_path)
    if not audio_file.exists():
        console.print(f"[red]Error: File not found: {audio_path}[/red]")
        return None

    try:
        url = ENDPOINTS["audio_transcription"]

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        files = {
            "file": (audio_file.name, open(audio_path, "rb"), "audio/mpeg")
        }

        data = {
            "model": Models.AUDIO_ASR,
            "stream": "false",
            "timestamp_granularities": "segment"
        }

        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()

        result = response.json()

        console.print(Panel(
            result.get("text", "No transcription"),
            title="Full Transcription",
            border_style="green"
        ))

        return result

    except Exception as e:
        print_error(e, "Timestamp transcription failed")
        return None


def demo_multilingual():
    """Demo: Transcription with different language hints."""
    console.print(Panel.fit(
        "[bold cyan]Multilingual Transcription Demo[/bold cyan]\n"
        "Supported: Chinese, English, French, German, Japanese, Korean",
        border_style="cyan"
    ))

    console.print("\n[yellow]To run this demo, provide audio files for each language:[/yellow]")

    languages = [
        ("zh", "Chinese", "mandarin_sample.mp3"),
        ("en", "English", "english_sample.mp3"),
        ("ja", "Japanese", "japanese_sample.mp3"),
        ("ko", "Korean", "korean_sample.mp3"),
        ("de", "German", "german_sample.mp3"),
        ("fr", "French", "french_sample.mp3"),
    ]

    table = Table(title="Supported Languages")
    table.add_column("Code", style="cyan")
    table.add_column("Language", style="green")
    table.add_column("Sample File", style="dim")

    for code, name, sample in languages:
        table.add_row(code, name, sample)

    console.print(table)

    console.print("\n[dim]Usage: python audio_transcription.py -f your_audio.mp3 -l en[/dim]")


def check_audio_file(audio_path: str):
    """
    Check if an audio file meets the API requirements.

    Args:
        audio_path: Path to the audio file
    """
    console.print(Panel.fit(
        "[bold cyan]Audio File Check[/bold cyan]\n"
        "Verify file meets API requirements",
        border_style="cyan"
    ))

    audio_file = Path(audio_path)

    if not audio_file.exists():
        console.print(f"[red]File not found: {audio_path}[/red]")
        return False

    file_size = audio_file.stat().st_size / (1024 * 1024)
    extension = audio_file.suffix.lower()

    table = Table(title="File Analysis")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Status", style="green")

    # File size check
    size_status = "[green]OK[/green]" if file_size <= 25 else "[red]TOO LARGE[/red]"
    table.add_row("Size", f"{file_size:.2f} MB", size_status)

    # Format check
    supported_formats = [".mp3", ".wav", ".m4a", ".webm", ".flac", ".ogg"]
    format_status = "[green]OK[/green]" if extension in supported_formats else "[yellow]UNKNOWN[/yellow]"
    table.add_row("Format", extension, format_status)

    # File name
    table.add_row("Name", audio_file.name, "")

    console.print(table)

    # Duration note
    console.print("\n[dim]Note: Audio must be ≤30 seconds. Duration cannot be checked without additional libraries.[/dim]")

    return file_size <= 25 and extension in supported_formats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Audio Transcription")
    parser.add_argument("-f", "--file", type=str, help="Path to audio file")
    parser.add_argument("-l", "--language", type=str,
                        help="Language hint (zh, en, ja, ko, de, fr)")
    parser.add_argument("--timestamps", action="store_true",
                        help="Include detailed timestamps")
    parser.add_argument("--check", action="store_true",
                        help="Check if file meets requirements")
    parser.add_argument("--demo-languages", action="store_true",
                        help="Show supported languages")

    args = parser.parse_args()

    if args.demo_languages:
        demo_multilingual()
    elif args.file:
        if args.check:
            check_audio_file(args.file)
        elif args.timestamps:
            transcribe_with_timestamps(args.file)
        else:
            run(args.file, language=args.language)
    else:
        console.print("[yellow]Please provide an audio file with -f/--file[/yellow]")
        console.print("[dim]Example: python audio_transcription.py -f sample.mp3[/dim]")
        console.print("\n[dim]Or run --demo-languages to see supported languages[/dim]")
