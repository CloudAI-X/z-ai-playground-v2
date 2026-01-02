"""
Object Detection Example
Demonstrates GLM-4.6V's ability to detect objects and return bounding boxes.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[2]))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Models, get_sample_images, load_image_as_data_url, SAMPLE_IMAGE_PATHS
from utils.client import get_client, print_error

console = Console()


def run(image_url: str = None, target_objects: str = None):
    """
    Detect objects in an image and return bounding boxes.

    Args:
        image_url: URL of the image to analyze
        target_objects: Specific objects to detect (or "all" for general detection)
    """
    console.print(Panel.fit(
        "[bold cyan]Object Detection Example[/bold cyan]\n"
        f"Model: {Models.VLM}\n"
        "Detecting objects with bounding box coordinates",
        border_style="cyan"
    ))

    image_url = image_url or load_image_as_data_url(SAMPLE_IMAGE_PATHS["detection"])
    target = target_objects or "all visible objects"

    console.print(f"\n[bold]Image URL:[/bold] {image_url[:60]}...")
    console.print(f"[bold]Target:[/bold] {target}\n")

    try:
        client = get_client()

        prompt = f"""Detect {target} in this image.
Return the results in valid JSON format as a list where each element contains:
- "label": the object name/description
- "bbox_2d": bounding box coordinates as [xmin, ymin, xmax, ymax]
- "confidence": estimated confidence (high/medium/low)

Example format:
[
  {{"label": "Person", "bbox_2d": [100, 150, 300, 500], "confidence": "high"}},
  {{"label": "Car", "bbox_2d": [400, 200, 600, 350], "confidence": "medium"}}
]

Only return the JSON, no other text."""

        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }]

        console.print("[dim]Detecting objects...[/dim]\n")

        response = client.create_chat(
            messages=messages,
            model=Models.VLM,
            thinking={"type": "enabled"},
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        # Try to parse as JSON
        try:
            # Handle potential markdown code blocks
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            detections = json.loads(content)

            if isinstance(detections, list):
                # Display results in a table
                table = Table(title="Detected Objects")
                table.add_column("Label", style="cyan")
                table.add_column("Bounding Box", style="green")
                table.add_column("Confidence", style="yellow")

                for det in detections:
                    label = det.get("label", "Unknown")
                    bbox = det.get("bbox_2d", [])
                    conf = det.get("confidence", "N/A")
                    table.add_row(label, str(bbox), conf)

                console.print(table)
                console.print(f"\n[dim]Total objects detected: {len(detections)}[/dim]")

                return detections

            else:
                console.print(Panel(content, title="Detection Result", border_style="green"))
                return detections

        except json.JSONDecodeError:
            console.print("[yellow]Could not parse as JSON. Raw response:[/yellow]")
            console.print(Panel(content, title="Raw Response", border_style="yellow"))
            return content

    except Exception as e:
        print_error(e, "Object detection failed")
        return None


def run_with_grounding(image_url: str = None, target: str = None):
    """
    Detect a specific object and get its grounding coordinates.

    Args:
        image_url: URL of the image
        target: Specific object to locate (e.g., "the red button", "second person from left")
    """
    console.print(Panel.fit(
        "[bold cyan]Visual Grounding Example[/bold cyan]\n"
        "Locating specific objects with natural language",
        border_style="cyan"
    ))

    image_url = image_url or load_image_as_data_url(SAMPLE_IMAGE_PATHS["detection"])
    target = target or "the most prominent object"

    console.print(f"\n[bold]Target:[/bold] {target}\n")

    try:
        client = get_client()

        prompt = f"""Find "{target}" in this image.
Provide the coordinates in [[xmin, ymin, xmax, ymax]] format.
Explain briefly why you identified this as the target."""

        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }]

        response = client.create_chat(
            messages=messages,
            model=Models.VLM,
            stream=True,
            thinking={"type": "enabled"}
        )

        result = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    result += delta.content
                    console.print(delta.content, end="", markup=False)

        console.print("\n")
        return result

    except Exception as e:
        print_error(e, "Grounding failed")
        return None


def demo_counting():
    """Demo: Count specific types of objects in an image."""
    console.print(Panel.fit(
        "[bold cyan]Object Counting Demo[/bold cyan]\n"
        "Counting objects in images",
        border_style="cyan"
    ))

    client = get_client()
    image_url = load_image_as_data_url(SAMPLE_IMAGE_PATHS["detection"])

    prompt = """Count all distinct objects in this image.
Return a JSON object with:
- "total_count": total number of objects
- "categories": object of category names to counts
- "details": list of each object with position

Be thorough and count everything visible."""

    try:
        messages = [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": prompt}
            ]
        }]

        response = client.create_chat(
            messages=messages,
            model=Models.VLM,
            thinking={"type": "enabled"}
        )

        console.print(Panel(
            response.choices[0].message.content,
            title="Counting Results",
            border_style="green"
        ))

    except Exception as e:
        print_error(e, "Counting demo failed")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Object Detection Example")
    parser.add_argument("-u", "--url", type=str, help="Image URL to analyze")
    parser.add_argument("-t", "--target", type=str,
                        help="Specific objects to detect")
    parser.add_argument("--grounding", action="store_true",
                        help="Run visual grounding mode")
    parser.add_argument("--demo-counting", action="store_true",
                        help="Run object counting demo")

    args = parser.parse_args()

    if args.grounding:
        run_with_grounding(image_url=args.url, target=args.target)
    elif args.demo_counting:
        demo_counting()
    else:
        run(image_url=args.url, target_objects=args.target)
