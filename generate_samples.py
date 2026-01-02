"""
Generate sample images for VLM examples.
"""

import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel

from config import API_KEY, BASE_URL, Models

console = Console()

# Output directory
IMAGES_DIR = Path(__file__).parent / "images"

# Image prompts for VLM examples
IMAGE_PROMPTS = {
    "image_understanding.jpg": "A serene Japanese garden with a wooden bridge over a koi pond, cherry blossom trees in full bloom, traditional stone lanterns, and a small pagoda in the background. Morning light filtering through the trees.",

    "multi_image_1.jpg": "A modern minimalist living room with a white sofa, wooden coffee table, large windows with natural light, indoor plants, and abstract wall art. Clean Scandinavian design aesthetic.",

    "multi_image_2.jpg": "A cozy traditional living room with a brown leather couch, vintage wooden furniture, brick fireplace, warm lighting from table lamps, and bookshelves filled with books. Rustic cottage style.",

    "object_detection.jpg": "A busy city street scene with pedestrians crossing a crosswalk, cars and taxis parked along the road, street signs, traffic lights, a food cart vendor, bicycles, and storefronts with colorful awnings. Clear daylight, multiple distinct objects visible.",
}


def generate_image(prompt: str, filename: str):
    """Generate an image and save it to the images folder."""
    console.print(f"\n[bold]Generating:[/bold] {filename}")
    console.print(f"[dim]Prompt: {prompt[:60]}...[/dim]")
    
    url = BASE_URL + "images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": Models.IMAGE_GEN,
        "prompt": prompt,
        "size": "1024x1024"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if "data" in result and result["data"]:
            image_url = result["data"][0].get("url")
            if image_url:
                # Download the image
                img_response = requests.get(image_url, timeout=60)
                img_response.raise_for_status()
                
                # Save to file
                output_path = IMAGES_DIR / filename
                with open(output_path, "wb") as f:
                    f.write(img_response.content)
                
                console.print(f"[green]Saved:[/green] {output_path}")
                return str(output_path)
        
        console.print(f"[red]No image URL in response[/red]")
        return None
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None


def run():
    """Generate all sample images."""
    console.print(Panel.fit(
        "[bold cyan]Generating Sample Images[/bold cyan]\n"
        f"Output: {IMAGES_DIR}",
        border_style="cyan"
    ))

    IMAGES_DIR.mkdir(exist_ok=True)

    results = {}
    for filename, prompt in IMAGE_PROMPTS.items():
        result = generate_image(prompt, filename)
        results[filename] = result
        time.sleep(2)  # Rate limiting

    console.print("\n[bold]Summary:[/bold]")
    for filename, path in results.items():
        status = "[green]OK[/green]" if path else "[red]FAILED[/red]"
        console.print(f"  {filename}: {status}")

    console.print("\n[bold green]Done![/bold green]")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample images for VLM examples")
    parser.add_argument("--images", action="store_true", help="Generate images (default)")

    args = parser.parse_args()
    run()
