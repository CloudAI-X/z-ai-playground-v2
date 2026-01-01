"""
Audio Model Examples (GLM-ASR-2512)
Demonstrates audio transcription and streaming transcription.
"""

from .audio_transcription import run as run_transcription
from .streaming_transcription import run as run_streaming_transcription

__all__ = [
    "run_transcription",
    "run_streaming_transcription",
]
