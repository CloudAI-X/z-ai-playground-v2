# Z.AI API Playground

> **Powered by [Z.AI-GLM-4.7-Coding Plan](https://z.ai/subscribe)**

Complete examples for Z.AI's API including GLM-4.7 chat, vision, image/video generation, audio transcription, and more.

## Features

| Category | Model | Examples |
|----------|-------|----------|
| **Chat** | GLM-4.7 | Basic, streaming, multi-turn, thinking mode |
| **Vision** | GLM-4.6V | Image understanding, object detection, video analysis |
| **Image Gen** | CogView-4 | Text-to-image generation |
| **Video Gen** | CogVideoX-3 | Text-to-video, image-to-video, start/end frame |
| **Audio** | GLM-ASR-2512 | Transcription, streaming transcription |
| **Tools** | GLM-4.7 | Function calling, web search, structured output |

## GLM-4.7 Best Practices Applied

- `temperature=1.0` - Default sampling parameter
- `max_tokens` - Configurable up to 128K output
- `tool_stream=True` - Streaming tool call arguments
- `thinking={"type": "enabled"}` - Deep reasoning mode

## Quick Start

```bash
# Install dependencies
uv sync

# Set your API key
export Z_AI_API_KEY="your-api-key"

# Run examples
python examples/01_llm/basic_chat.py
python examples/06_capabilities/function_calling.py --demo-streaming
```

## Project Structure

```
examples/
├── 01_llm/          # Chat completions
├── 02_vlm/          # Vision/multimodal
├── 03_image/        # Image generation
├── 04_video/        # Video generation
├── 05_audio/        # Audio transcription
├── 06_capabilities/ # Function calling, JSON mode
├── 07_tools/        # Web search
└── 08_agents/       # Multi-function agents

http_examples/       # Direct HTTP API examples
utils/               # Shared client utilities
```

## Using GLM-4.7 with Claude Code

This project was built using **GLM-4.7 inside Claude Code** via the Z.AI-GLM-4.7-Coding Plan. Here's how to set it up:

### Setup Instructions

1. **Subscribe to Z.AI-GLM-4.7-Coding Plan** at [z.ai/subscribe](https://z.ai/subscribe)

2. **Configure Claude Code** - Add to your `~/.claude/settings.json`:

```json
{
  "primaryApiKey": "YOUR_Z_AI_API_KEY",
  "apiKeyHelper": "",
  "primaryApiKeySource": "Settings file",
  "apiProvider": "openai",
  "apiUrl": "https://api.z.ai/api/coding/paas/v4/",
  "model": "glm-4.7",
  "maxTokens": 16000,
  "temperature": 1.0
}
```

3. **Verify Configuration**:
```bash
claude config list
```

### Key Configuration Details

| Setting | Value | Description |
|---------|-------|-------------|
| `apiProvider` | `"openai"` | Z.AI uses OpenAI-compatible API |
| `apiUrl` | `https://api.z.ai/api/coding/paas/v4/` | Z.AI Coding Plan endpoint |
| `model` | `"glm-4.7"` | GLM-4.7 model for advanced reasoning |
| `temperature` | `1.0` | GLM-4.7 recommended default |
| `maxTokens` | `16000` | Adjust as needed (max 128K) |

### Why Z.AI-GLM-4.7-Coding Plan?

- **Cost-effective**: Best value for AI coding assistance
- **128K output tokens**: Handle large codebases
- **200K context window**: Understand complex projects
- **Deep reasoning**: `thinking` mode for complex problems
- **OpenAI-compatible**: Works with Claude Code seamlessly

## Credits

This project is powered by **[Z.AI-GLM-4.7-Coding Plan](https://z.ai/subscribe)** - the most cost-effective way to access GLM-4.7's advanced coding capabilities.

## License

MIT
