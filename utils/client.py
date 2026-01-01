"""
Shared Z.AI Client Module
Provides reusable client initialization with proper error handling.
"""

import sys
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from config import API_KEY, BASE_URL, Models, Defaults

console = Console()

# Lazy import to avoid circular dependency
_client = None


class ZaiClientWrapper:
    """Wrapper for ZaiClient with convenience methods and error handling."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        from zai import ZaiClient

        self.api_key = api_key or API_KEY
        self.base_url = base_url or BASE_URL
        self._client = ZaiClient(api_key=self.api_key, base_url=self.base_url)

    @property
    def client(self):
        """Get the underlying ZaiClient instance."""
        return self._client

    @property
    def chat(self):
        """Access chat completions."""
        return self._client.chat

    @property
    def images(self):
        """Access image generation."""
        return self._client.images

    @property
    def videos(self):
        """Access video generation."""
        return self._client.videos

    @property
    def web_search(self):
        """Access web search."""
        return self._client.web_search

    def create_chat(
        self,
        messages: list,
        model: str = Models.LLM,
        stream: bool = False,
        thinking: Optional[dict] = None,
        tools: Optional[list] = None,
        tool_stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ):
        """
        Create a chat completion with sensible defaults.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: GLM-4.7)
            stream: Enable streaming response
            thinking: Thinking mode config (e.g., {"type": "enabled"})
            tools: List of tool definitions for function calling
            tool_stream: Enable streaming tool call arguments (requires stream=True)
            temperature: Sampling temperature (0.0-2.0). Do NOT use with top_p.
            max_tokens: Maximum output tokens (up to 128K for GLM-4.7)
            **kwargs: Additional parameters passed to the API

        Note:
            GLM-4.7 Best Practice: Use either 'temperature' OR 'top_p', never both.
            GLM-4.7 supports 128K max output tokens and 200K context window.
        """
        params = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        # Apply sampling parameters
        if temperature is not None:
            params["temperature"] = temperature

        if max_tokens is not None:
            params["max_tokens"] = max_tokens

        if thinking is not None:
            params["thinking"] = thinking

        if tools is not None:
            params["tools"] = tools
            params["tool_choice"] = kwargs.pop("tool_choice", "auto")
            # Enable tool_stream for streaming tool parameters (GLM-4.7 feature)
            if stream and tool_stream:
                params["tool_stream"] = True

        params.update(kwargs)

        return self._client.chat.completions.create(**params)

    def create_streaming_chat_with_tools(
        self,
        messages: list,
        tools: list,
        model: str = Models.LLM,
        temperature: float = Defaults.TEMPERATURE,
        max_tokens: Optional[int] = None,
        thinking: Optional[dict] = None,
        **kwargs,
    ) -> tuple:
        """
        Create a streaming chat with tool support and proper argument concatenation.

        This implements the GLM-4.7 best practice pattern for streaming tool calls,
        where tool arguments are concatenated across chunks.

        Args:
            messages: List of message dicts
            tools: List of tool definitions
            model: Model to use
            temperature: Sampling temperature (default: 1.0)
            max_tokens: Maximum output tokens
            thinking: Thinking mode config
            **kwargs: Additional parameters

        Returns:
            tuple: (content, reasoning, tool_calls_dict)
            - content: The text response
            - reasoning: The reasoning content (if thinking enabled)
            - tool_calls_dict: {index: tool_call_info} with concatenated arguments
        """
        response = self.create_chat(
            messages=messages,
            model=model,
            stream=True,
            tools=tools,
            tool_stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
            **kwargs,
        )

        content = ""
        reasoning = ""
        tool_calls = {}

        for chunk in response:
            if not chunk.choices or not chunk.choices[0].delta:
                continue

            delta = chunk.choices[0].delta

            # Handle reasoning content
            if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                reasoning += delta.reasoning_content

            # Handle regular content
            if hasattr(delta, "content") and delta.content:
                content += delta.content

            # Handle streaming tool calls with argument concatenation
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls:
                        # Initialize new tool call
                        tool_calls[idx] = {
                            "id": tc.id,
                            "function": {
                                "name": tc.function.name or "",
                                "arguments": tc.function.arguments or "",
                            },
                        }
                    else:
                        # Concatenate arguments (key GLM-4.7 pattern)
                        if tc.function.arguments:
                            tool_calls[idx]["function"]["arguments"] += tc.function.arguments

        return content, reasoning, tool_calls

    def generate_image(
        self,
        prompt: str,
        model: str = Models.IMAGE_GEN,
        size: str = "1024x1024",
        **kwargs,
    ):
        """
        Generate an image from text prompt.

        Args:
            prompt: Text description of the image to generate
            model: Model to use (default: CogView-4)
            size: Image size (default: 1024x1024)
            **kwargs: Additional parameters
        """
        return self._client.images.generations(
            model=model,
            prompt=prompt,
            size=size,
            **kwargs,
        )

    def generate_video(
        self,
        prompt: str,
        model: str = Models.VIDEO_GEN,
        quality: str = "quality",
        size: str = "1920x1080",
        fps: int = 30,
        with_audio: bool = True,
        image_url: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate a video from text or image.

        Args:
            prompt: Text description of the video
            model: Model to use (default: CogVideoX-3)
            quality: "quality" or "speed"
            size: Video resolution (up to 4K)
            fps: Frame rate (30 or 60)
            with_audio: Include audio in output
            image_url: Optional source image URL for image-to-video
            **kwargs: Additional parameters
        """
        params = {
            "model": model,
            "prompt": prompt,
            "quality": quality,
            "size": size,
            "fps": fps,
            "with_audio": with_audio,
        }

        if image_url:
            params["image_url"] = image_url

        params.update(kwargs)

        return self._client.videos.generations(**params)

    def retrieve_video_result(self, video_id: str):
        """
        Retrieve the result of a video generation job.

        Args:
            video_id: The ID returned from generate_video()
        """
        return self._client.videos.retrieve_videos_result(id=video_id)


def get_client(
    api_key: Optional[str] = None, base_url: Optional[str] = None
) -> ZaiClientWrapper:
    """
    Get a configured ZaiClient wrapper instance.

    Uses singleton pattern for efficiency unless custom params are provided.

    Args:
        api_key: Optional custom API key
        base_url: Optional custom base URL

    Returns:
        ZaiClientWrapper instance
    """
    global _client

    # Return cached client if using defaults
    if api_key is None and base_url is None:
        if _client is None:
            _client = ZaiClientWrapper()
        return _client

    # Create new client for custom params
    return ZaiClientWrapper(api_key=api_key, base_url=base_url)


def print_response(response, title: str = "Response"):
    """Pretty print an API response using Rich with Markdown rendering."""
    if hasattr(response, "choices") and response.choices:
        content = response.choices[0].message.content or ""
        # Render as Markdown for proper formatting
        rendered = Markdown(content) if content else ""
        console.print(Panel(rendered, title=title, border_style="green"))

        # Show reasoning if present
        if hasattr(response.choices[0].message, "reasoning_content"):
            reasoning = response.choices[0].message.reasoning_content
            if reasoning:
                console.print(
                    Panel(Markdown(reasoning), title="Reasoning", border_style="blue")
                )

        # Show usage stats
        if hasattr(response, "usage") and response.usage:
            usage = response.usage
            console.print(
                f"[dim]Tokens: {usage.prompt_tokens} prompt + "
                f"{usage.completion_tokens} completion = {usage.total_tokens} total[/dim]"
            )
    else:
        console.print(Panel(str(response), title=title, border_style="yellow"))


def print_error(error: Exception, context: str = ""):
    """Pretty print an error message."""
    msg = f"{context}: {error}" if context else str(error)
    console.print(Panel(msg, title="Error", border_style="red"))
