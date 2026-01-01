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

This project was built using **GLM-4.7 inside Claude Code** via the [Z.AI-GLM-4.7-Coding Plan](https://z.ai/subscribe).

> **Why GLM Coding Plan?** Get 3× the usage at a fraction of the cost. Code faster, debug smarter, and manage workflows seamlessly with more tokens and rock-solid reliability.

### Step 1: Install Claude Code

**Prerequisites:** [Node.js 18 or newer](https://nodejs.org/en/download/)

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Navigate to your project
cd your-awesome-project

# Start Claude Code
claude
```

> **Note:** If you encounter permission issues, use `sudo` (macOS/Linux) or run as administrator (Windows).

### Step 2: Configure GLM Coding Plan

1. **Get API Key**
   - Register/Login at [Z.AI Open Platform](https://z.ai/model-api)
   - Create an API Key at [API Keys](https://z.ai/manage-apikey/apikey-list)
   - Copy your API Key

2. **Configure Environment** (choose one method):

#### Option A: Automated Setup (Recommended)

```bash
# Run the Coding Tool Helper
npx @z_ai/coding-helper
```

#### Option B: Automated Script (macOS/Linux)

```bash
curl -O "https://cdn.bigmodel.cn/install/claude_code_zai_env.sh" && bash ./claude_code_zai_env.sh
```

#### Option C: Manual Configuration

Edit `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "your_zai_api_key",
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

**Windows (Cmd):**
```cmd
setx ANTHROPIC_AUTH_TOKEN your_zai_api_key
setx ANTHROPIC_BASE_URL https://api.z.ai/api/anthropic
```

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_AUTH_TOKEN', 'your_zai_api_key', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_BASE_URL', 'https://api.z.ai/api/anthropic', 'User')
```

### Step 3: Start Using Claude Code

```bash
cd your-project-directory
claude
```

Grant file access permission when prompted, and you're ready to code!

### Model Mapping

| Claude Code Model | GLM Model |
|-------------------|-----------|
| Opus | GLM-4.7 |
| Sonnet | GLM-4.7 |
| Haiku | GLM-4.5-Air |

To customize model mapping, add to `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7"
  }
}
```

Check current model with `/status` command in Claude Code.

### Why Z.AI-GLM-4.7-Coding Plan?

- **3× more usage** at a fraction of the cost
- **128K output tokens** for large codebases
- **200K context window** for complex projects
- **Deep reasoning** with thinking mode
- **Rock-solid reliability**

## Credits

This project is powered by **[Z.AI-GLM-4.7-Coding Plan](https://z.ai/subscribe)** - the most cost-effective way to access GLM-4.7's advanced coding capabilities.

## License

MIT
