#!/usr/bin/env python3
"""
Z.AI API Explorer
Interactive CLI menu for exploring all Z.AI API capabilities.
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

console = Console()

MENU = """
[bold cyan]╔══════════════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]                    [bold white]Z.AI API Explorer[/bold white]                           [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]LANGUAGE MODELS (GLM-4.7)[/bold yellow]                                      [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]1.[/cyan] Basic Chat                                                 [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]2.[/cyan] Streaming Chat                                             [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]3.[/cyan] Multi-turn Conversation                                    [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]4.[/cyan] Thinking Mode (Deep Reasoning)                             [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]VISION LANGUAGE MODELS (GLM-4.6V)[/bold yellow]                              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]5.[/cyan] Image Understanding                                        [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]6.[/cyan] Multi-Image Analysis                                       [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]7.[/cyan] Video Understanding                                        [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]8.[/cyan] Object Detection                                           [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]IMAGE GENERATION (CogView-4)[/bold yellow]                                   [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]    [cyan]9.[/cyan] Text-to-Image Generation                                   [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]VIDEO GENERATION (CogVideoX-3)[/bold yellow]                                 [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]10.[/cyan] Text-to-Video                                              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]11.[/cyan] Image-to-Video                                             [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]12.[/cyan] Start/End Frame Video                                      [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]AUDIO MODELS (GLM-ASR-2512)[/bold yellow]                                    [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]13.[/cyan] Audio Transcription                                        [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]14.[/cyan] Streaming Transcription                                    [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]ADVANCED CAPABILITIES[/bold yellow]                                          [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]15.[/cyan] Function Calling                                           [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]16.[/cyan] Structured Output (JSON)                                   [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]17.[/cyan] Web Search API                                             [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]18.[/cyan] Web Search in Chat                                         [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]AGENTS[/bold yellow]                                                         [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]19.[/cyan] Multi-Function Agent                                       [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]HTTP API EXAMPLES[/bold yellow]                                              [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]20.[/cyan] HTTP Chat Completion                                       [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]21.[/cyan] HTTP Image Generation                                      [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]   [cyan]22.[/cyan] HTTP Video Generation                                      [bold cyan]║[/bold cyan]
[bold cyan]╠══════════════════════════════════════════════════════════════════╣[/bold cyan]
[bold cyan]║[/bold cyan]    [red]0.[/red] Exit                                                        [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════════════╝[/bold cyan]
"""


def run_example(choice: int):
    """Run the selected example."""
    import importlib

    # Map choices to module paths
    module_map = {
        1: ("examples.01_llm.basic_chat", "run"),
        2: ("examples.01_llm.streaming_chat", "run"),
        3: ("examples.01_llm.multi_turn_chat", "run"),
        4: ("examples.01_llm.thinking_mode", "run"),
        5: ("examples.02_vlm.image_understanding", "run"),
        6: ("examples.02_vlm.multi_image_analysis", "run"),
        7: ("examples.02_vlm.video_understanding", "run"),
        8: ("examples.02_vlm.object_detection", "run"),
        9: ("examples.03_image.cogview4_generation", "run"),
        10: ("examples.04_video.text_to_video", "run"),
        11: ("examples.04_video.image_to_video", "run"),
        12: ("examples.04_video.start_end_frame", "run"),
        15: ("examples.06_capabilities.function_calling", "run"),
        16: ("examples.06_capabilities.structured_output", "run"),
        17: ("examples.07_tools.web_search_api", "run"),
        18: ("examples.07_tools.web_search_chat", "run"),
        19: ("examples.08_agents.multi_function_agent", "run"),
        20: ("http_examples.chat_completion", "run"),
        21: ("http_examples.image_generation", "run"),
        22: ("http_examples.video_generation", "show_async_pattern"),
    }

    try:
        if choice == 13:
            console.print("[yellow]Audio transcription requires an audio file.[/yellow]")
            console.print("[dim]Run: python examples/05_audio/audio_transcription.py -f your_audio.mp3[/dim]")
        elif choice == 14:
            console.print("[yellow]Streaming transcription requires an audio file.[/yellow]")
            console.print("[dim]Run: python examples/05_audio/streaming_transcription.py -f your_audio.mp3[/dim]")
        elif choice in module_map:
            module_path, func_name = module_map[choice]
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            func()

            if choice == 22:
                console.print("\n[dim]For actual video generation, run:[/dim]")
                console.print("[dim]python http_examples/video_generation.py -p 'your prompt'[/dim]")
        else:
            console.print("[red]Invalid choice[/red]")
    except ImportError as e:
        console.print(f"[red]Error importing module: {e}[/red]")
        console.print("[dim]Make sure all dependencies are installed.[/dim]")


def show_info():
    """Show information about the project."""
    table = Table(title="Z.AI API Models")
    table.add_column("Category", style="cyan")
    table.add_column("Model", style="green")
    table.add_column("Use Case", style="white")

    table.add_row("Language", "GLM-4.7", "Chat, reasoning, code generation")
    table.add_row("Vision", "GLM-4.6V", "Image/video understanding")
    table.add_row("Image Gen", "CogView-4", "Text-to-image ($0.01/image)")
    table.add_row("Video Gen", "CogVideoX-3", "Text/image-to-video ($0.2/video)")
    table.add_row("Audio", "GLM-ASR-2512", "Speech-to-text transcription")

    console.print(table)


def main():
    """Main entry point."""
    console.print(Panel.fit(
        "[bold white]Welcome to the Z.AI API Explorer![/bold white]\n"
        "Explore every capability of the Z.AI platform.",
        border_style="cyan"
    ))

    # Check for API key
    try:
        from config import API_KEY
        if not API_KEY:
            console.print("[red]Warning: Z_AI_API_KEY not found in .env[/red]")
            console.print("[dim]Please add your API key to the .env file[/dim]")
    except ImportError:
        console.print("[red]Error: config.py not found[/red]")
        return

    while True:
        console.print(MENU)
        show_info()

        try:
            choice = IntPrompt.ask("\n[bold]Select an option[/bold]", default=0)

            if choice == 0:
                console.print("\n[bold cyan]Goodbye! Happy coding with Z.AI![/bold cyan]\n")
                break

            console.print()
            run_example(choice)

            console.print()
            Prompt.ask("[dim]Press Enter to continue...[/dim]")
            console.clear()

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]Goodbye![/bold cyan]\n")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
