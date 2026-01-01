"""
Vision Language Model Examples (GLM-4.6V)
Demonstrates image understanding, multi-image analysis, video understanding, and object detection.
"""

from .image_understanding import run as run_image_understanding
from .multi_image_analysis import run as run_multi_image_analysis
from .video_understanding import run as run_video_understanding
from .object_detection import run as run_object_detection

__all__ = [
    "run_image_understanding",
    "run_multi_image_analysis",
    "run_video_understanding",
    "run_object_detection",
]
