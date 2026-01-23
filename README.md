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

# GLM-4.7 — Your New Coding Partner

GLM-4.7 is a next-generation AI coding model designed to deliver measurable improvements across coding, reasoning, tool usage, and creative tasks. Compared to GLM-4.6, it demonstrates significant gains across multilingual coding, agent workflows, and terminal-based tasks.

---

## Key Features

### Core Coding
GLM-4.7 shows clear improvements over GLM-4.6 in multilingual agentic coding and terminal-based workflows:

- **SWE-bench Verified:** 73.8% (+5.8%)
- **SWE-bench Multilingual:** 66.7% (+12.9%)
- **Terminal Bench 2.0:** 41.0% (+16.5%)

The model supports **thinking before acting**, enabling improved performance on complex tasks in mainstream agent frameworks such as Claude Code, Kilo Code, Cline, and Roo Code.

---

### Vibe Coding (UI & Design Quality)
GLM-4.7 takes a major step forward in UI and design outputs:

- Produces cleaner and more modern webpages  
- Generates better-looking slides with improved layout accuracy and sizing consistency  

---

### Tool Usage
GLM-4.7 significantly improves tool-use capabilities, with stronger performance on:

- **τ²-Bench**
- **BrowseComp (web browsing tasks)**

---

### Complex Reasoning
GLM-4.7 delivers substantial improvements in mathematical and logical reasoning:

- **HLE (Humanity’s Last Exam):** 42.8% (+12.4%) with tools  

---

### Additional Improvements
GLM-4.7 also shows strong gains across:

- Chat and conversational tasks  
- Creative writing  
- Role-play and simulation scenarios  

---

## Benchmark Performance

Detailed comparisons of GLM-4.7 against leading models (GPT-5, GPT-5.1-High, Claude Sonnet 4.5, Gemini 3.0 Pro, DeepSeek-V3.2, Kimi K2 Thinking) across 17 benchmarks are summarized below.

### Reasoning Benchmarks

| Benchmark | GLM-4.7 | GLM-4.6 | Kimi K2 Thinking | DeepSeek-V3.2 | Gemini 3.0 Pro | Claude Sonnet 4.5 | GPT-5 High | GPT-5.1 High |
|-----------|----------|----------|------------------|----------------|----------------|-------------------|------------|--------------|
| MMLU-Pro | 84.3 | 83.2 | 84.6 | 85.0 | 90.1 | 88.2 | 87.5 | 87.0 |
| GPQA-Diamond | 85.7 | 81.0 | 84.5 | 82.4 | 91.9 | 83.4 | 85.7 | 88.1 |
| HLE | 24.8 | 17.2 | 23.9 | 25.1 | 37.5 | 13.7 | 26.3 | 25.7 |
| HLE (w/ Tools) | 42.8 | 30.4 | 44.9 | 40.8 | 45.8 | 32.0 | 35.2 | 42.7 |
| AIME 2025 | 95.7 | 93.9 | 94.5 | 93.1 | 95.0 | 87.0 | 94.6 | 94.0 |
| HMMT Feb. 2025 | 97.1 | 89.2 | 89.4 | 92.5 | 97.5 | 79.2 | 88.3 | 96.3 |
| HMMT Nov. 2025 | 93.5 | 87.7 | 89.2 | 90.2 | 93.3 | 81.7 | 89.2 | - |
| IMOAnswerBench | 82.0 | 73.5 | 78.6 | 78.3 | 83.3 | 65.8 | 76.0 | - |
| LiveCodeBench-v6 | 84.9 | 82.8 | 83.1 | 83.3 | 90.7 | 64.0 | 87.0 | 87.0 |

---

### Code Agent Benchmarks

| Benchmark | GLM-4.7 | GLM-4.6 | Kimi K2 Thinking | DeepSeek-V3.2 | Gemini 3.0 Pro | Claude Sonnet 4.5 | GPT-5 High | GPT-5.1 High |
|-----------|----------|----------|------------------|----------------|----------------|-------------------|------------|--------------|
| SWE-bench Verified | 73.8 | 68.0 | 71.3 | 73.1 | 76.2 | 77.2 | 74.9 | 76.3 |
| SWE-bench Multilingual | 66.7 | 53.8 | 61.1 | 70.2 | - | 68.0 | 55.3 | - |
| Terminal Bench Hard | 33.3 | 23.6 | 30.6 | 35.4 | 39.0 | 33.3 | 30.5 | 43.0 |
| Terminal Bench 2.0 | 41.0 | 24.5 | 35.7 | 46.4 | 54.2 | 42.8 | 35.2 | 47.6 |

---

### General Agent Benchmarks

| Benchmark | GLM-4.7 | GLM-4.6 | Kimi K2 Thinking | DeepSeek-V3.2 | Gemini 3.0 Pro | Claude Sonnet 4.5 | GPT-5 High | GPT-5.1 High |
|-----------|----------|----------|------------------|----------------|----------------|-------------------|------------|--------------|
| BrowseComp | 52.0 | 45.1 | - | 51.4 | - | 24.1 | 54.9 | 50.8 |
| BrowseComp (w/ Context Manage) | 67.5 | 57.5 | 60.2 | 67.6 | 59.2 | - | - | - |
| BrowseComp-ZH | 66.6 | 49.5 | 62.3 | 65.0 | - | 42.4 | 63.0 | - |
| τ²-Bench | 87.4 | 75.2 | 74.3 | 85.3 | 90.7 | 87.2 | 82.4 | 82.7 |

---

## Philosophy

AGI is a long journey, and benchmarks are only one way to evaluate progress. While metrics provide necessary checkpoints, the most important metric is **how it feels to use the system**.

True intelligence is not just about test performance or speed—ultimately, the success of AGI will be measured by how seamlessly it integrates into everyday workflows.

This time, we are *coding* that future.

---



## GLM-4.7 Best Practices Applied

- `temperature=1.0` - Default sampling parameter
- `max_tokens` - Configurable up to 128K output
- `tool_stream=True` - Streaming tool call arguments
- `thinking={"type": "enabled"}` - Deep reasoning mode

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Set your API key (create .env file)
echo 'Z_AI_API_KEY=your-api-key' > .env

# 3. Generate sample images (required for vision examples)
uv run python generate_samples.py --images

# 4. Run any example
uv run python examples/01_llm/basic_chat.py
```

> **Important:** Always use `uv run python` (not just `python`) to ensure dependencies are available.

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
images/              # Sample images for VLM examples
utils/               # Shared client utilities
```

## Vision Examples (GLM-4.6V)

### Before Running Vision Examples

**Step 1: Generate sample images first** (one-time setup):
```bash
uv run python generate_samples.py --images
```

This creates the `images/` folder with sample images used by vision examples.

### Running Vision Examples

All vision examples work out of the box after generating samples:

| Example | Command | What It Does |
|---------|---------|--------------|
| **Image Understanding** | `uv run python examples/02_vlm/image_understanding.py` | Analyzes a Japanese garden image |
| **Multi-Image Analysis** | `uv run python examples/02_vlm/multi_image_analysis.py` | Compares two living room images |
| **Object Detection** | `uv run python examples/02_vlm/object_detection.py` | Detects objects in a city street scene |
| **Video Understanding** | `uv run python examples/02_vlm/video_understanding.py` | Analyzes a sample video (uses built-in URL) |

### Using Your Own Images

```bash
# Analyze your own image
uv run python examples/02_vlm/image_understanding.py -u "https://example.com/your-image.jpg"

# Or use a local file (automatically converted to base64)
uv run python examples/02_vlm/image_understanding.py -u "path/to/local/image.jpg"
```

### Using Your Own Videos

> **Note:** Video analysis requires a **publicly accessible HTTP URL**. Local files and base64 are NOT supported for videos.

```bash
# Analyze your own video (must be a public URL)
uv run python examples/02_vlm/video_understanding.py -u "https://example.com/your-video.mp4"
```

### Sample Files Reference

| File | Used By | Auto-Generated |
|------|---------|----------------|
| `images/image_understanding.jpg` | image_understanding.py | Yes |
| `images/multi_image_1.jpg` | multi_image_analysis.py | Yes |
| `images/multi_image_2.jpg` | multi_image_analysis.py | Yes |
| `images/object_detection.jpg` | object_detection.py | Yes |

### Programmatic Usage

```python
from config import load_image_as_data_url, get_sample_images

# Load a local image as base64 data URL
image_data = load_image_as_data_url("images/image_understanding.jpg")

# Or get pre-loaded sample images
sample_images = get_sample_images()  # Returns list of base64 data URLs

# Use with GLM-4.6V
messages = [{
    "role": "user",
    "content": [
        {"type": "image_url", "image_url": {"url": image_data}},
        {"type": "text", "text": "Describe this image"}
    ]
}]
```

## Video Generation Examples (CogVideoX-3)

### Running Video Generation Examples

| Example | Command | What It Does |
|---------|---------|--------------|
| **Text-to-Video** | `uv run python examples/04_video/text_to_video.py` | Generate video from text prompt |
| **Image-to-Video** | `uv run python examples/04_video/image_to_video.py` | Animate a static image |
| **Start/End Frame** | `uv run python examples/04_video/start_end_frame.py` | Create transition between two images |

> **Note:** Video generation costs $0.2 per video and takes 1-2 minutes to complete.

## Generating Sample Assets

```bash
# Generate sample images (required for vision examples)
uv run python generate_samples.py --images
```

## Interactive Menu

Run all examples from an interactive menu:

```bash
uv run python main.py
```

This launches a menu where you can select any example by number (1-22).

## Troubleshooting

### "No module named 'zai'" Error
Always use `uv run python` instead of just `python`:
```bash
# Wrong
python examples/02_vlm/image_understanding.py

# Correct
uv run python examples/02_vlm/image_understanding.py
```

### "Sample image not found" Error
Generate the sample images first:
```bash
uv run python generate_samples.py --images
```

### "Z_AI_API_KEY not found" Error
Create a `.env` file with your API key:
```bash
echo 'Z_AI_API_KEY=your-api-key-here' > .env
```

### Video Analysis Fails
Video understanding requires a **public HTTP URL**. Local files don't work for video analysis. The default example uses a built-in working URL.

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
