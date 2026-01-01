"""
Z.AI API Configuration Module
Centralized configuration for all API settings and model constants.
"""

import os
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


# Sample Data for Runnable Examples
SAMPLE_IMAGES = [
    "https://aigc-files.bigmodel.cn/api/cogview/20250723213827da171a419b9b4906_0.png",
    "https://cloudcovert-1305175928.cos.ap-guangzhou.myqcloud.com/%E5%9B%BE%E7%89%87grounding.PNG",
]

SAMPLE_VIDEO_FRAMES = {
    "first": "https://gd-hbimg.huaban.com/ccee58d77afe8f5e17a572246b1994f7e027657fe9e6-qD66In_fw1200webp",
    "last": "https://gd-hbimg.huaban.com/cc2601d568a72d18d90b2cc7f1065b16b2d693f7fa3f7-hDAwNq_fw1200webp",
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
