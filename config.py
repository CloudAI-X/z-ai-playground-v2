"""
Z.AI API Configuration Module
Centralized configuration for all API settings and model constants.
"""

import os
import base64
import functools
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_KEY = os.getenv("Z_AI_API_KEY")
BASE_URL = "https://api.z.ai/api/paas/v4/"
CODING_BASE_URL = "https://api.z.ai/api/coding/paas/v4"

# Model Constants - Target Models per User Request
class Models:
    # Language Models
    LLM = "glm-4.7"
    LLM_FLASH = "glm-4.5-flash"
    LLM_AIR = "glm-4.5-air"

    # Vision Language Models
    VLM = "glm-4.6v"
    VLM_FLASH = "glm-4.6v-flash"

    # Image Generation
    IMAGE_GEN = "cogView-4-250304"

    # Video Generation
    VIDEO_GEN = "cogvideox-3"

    # Audio Models
    AUDIO_ASR = "glm-asr-2512"


# GLM-4.7 Best Practice Defaults
class Defaults:
    """
    GLM-4.7 recommended parameter defaults.

    Best Practice: Use either temperature OR top_p, never both simultaneously.
    - temperature: Controls randomness (higher = more creative)
    - top_p: Controls nucleus sampling (higher = more diverse)
    """
    # Sampling Parameters (choose ONE)
    TEMPERATURE = 1.0        # Range: 0.0-2.0, default 1.0
    TOP_P = 0.95             # Range: 0.0-1.0, default 0.95

    # Token Limits
    MAX_TOKENS = 4096        # Reasonable default for most responses
    MAX_TOKENS_LONG = 8192   # For longer responses
    MAX_TOKENS_MAX = 128000  # GLM-4.7 maximum output

    # Context Window
    CONTEXT_WINDOW = 200000  # 200K context for GLM-4.7

    # Streaming
    TOOL_STREAM = True       # Enable streaming tool call parameters


# Project root directory
PROJECT_ROOT = Path(__file__).parent


def load_image_as_data_url(image_path: str | Path) -> str:
    """Convert a local image file to a base64 data URL."""
    path = Path(image_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(
            f"Sample image not found: {path}\n"
            f"Run 'python generate_samples.py' to generate sample images."
        )

    suffix = path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/jpeg")

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{data}"


# Local sample files
SAMPLE_IMAGE_PATHS = {
    "understanding": PROJECT_ROOT / "images" / "image_understanding.jpg",
    "multi_1": PROJECT_ROOT / "images" / "multi_image_1.jpg",
    "multi_2": PROJECT_ROOT / "images" / "multi_image_2.jpg",
    "detection": PROJECT_ROOT / "images" / "object_detection.jpg",
}


def get_sample_images() -> list[str]:
    """Get sample images as data URLs (for API usage)."""
    return [
        load_image_as_data_url(SAMPLE_IMAGE_PATHS["understanding"]),
        load_image_as_data_url(SAMPLE_IMAGE_PATHS["detection"]),
    ]


def get_multi_images() -> list[str]:
    """Get multi-image comparison samples as data URLs."""
    return [
        load_image_as_data_url(SAMPLE_IMAGE_PATHS["multi_1"]),
        load_image_as_data_url(SAMPLE_IMAGE_PATHS["multi_2"]),
    ]


# Sample Data for Runnable Examples
# Note: These are now local file paths. Use get_sample_images() to get base64 data URLs
# for API calls. These paths are kept for reference/debugging purposes.
SAMPLE_IMAGES = [
    str(SAMPLE_IMAGE_PATHS["understanding"]),
    str(SAMPLE_IMAGE_PATHS["detection"]),
]

# Sample image URLs for video generation (start/end frame)
# Note: Video generation requires HTTP URLs, not local files or base64
SAMPLE_VIDEO_FRAMES = {
    "first": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1920&q=80",
    "last": "https://images.unsplash.com/photo-1426604966848-d7adac402bff?w=1920&q=80",
}

TEST_PROMPTS = {
    "chat": "Explain quantum computing in simple terms, as if teaching a curious teenager.",
    "coding": "Write a Python function that checks if a number is prime.",
    "image_gen": "A serene Japanese garden at sunset with cherry blossoms, a wooden bridge over a koi pond, and Mount Fuji in the background. Photorealistic, 8K quality.",
    "video_gen": "A butterfly gently lands on a vibrant sunflower, its wings slowly opening and closing in the warm summer breeze.",
    "vision": "Describe this image in detail, including any text, objects, and their spatial relationships.",
    "detection": "Identify all objects in this image and return their bounding boxes in JSON format.",
}

# API Endpoints
ENDPOINTS = {
    "chat": "/chat/completions",
    "images": "/images/generations",
    "videos": "/videos/generations",
    "video_result": "/videos/{id}",
    "audio": "/audio/transcriptions",
    "web_search": "/web_search",
}

# Validate API Key on import
if not API_KEY:
    raise ValueError(
        "Z_AI_API_KEY not found in environment variables. "
        "Please set it in your .env file."
    )
