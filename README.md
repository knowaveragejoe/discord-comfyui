# 🤖ComfyUI Discord Bot

### A Discord bot for interacting with ComfyUI!

You'll need a ComfyUI setup with whatever nodes, models, etc already installed and configured.

The bot works by using ComfyUI workflows in API-compatible JSON format, templated with the user's input from discord.



## Setup

### Running the bog using Docker (Recommended)

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd discord-comfyui
   ```

2. Create a config directory and copy the template:
   ```bash
   mkdir config
   cp config.yaml.template config/config.yaml
   ```

3. Edit config/config.yaml with your:
   - Discord bot token
   - Guild ID
   - ComfyUI server details
   - Workflow configuration (there is a default workflow which is a simple checkpoint loader with positive/negative prompt)

4. Build and start the bot:
   ```bash
   docker compose up -d
   ```

### Manual Setup

You can also just run the bot manually.

1. Create a virtual environment and install the bot:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate
   uv sync
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with your Discord bot token and ComfyUI server details.

4. Run the bot:
   ```bash
   discord-comfyui
   ```

## Bot Configuration

You'll need a Discord developer account and a bot token. You can get this by creating a new application in the Discord Developer Portal.

Copy the config.yaml.template to config.yaml and follow the comments to configure the bot with this info.

## Workflow Configuration

This is probably the most important part of the entire bot.

The bot relies on a rather brittle system of using ComfyUI workflows, which can be completely arbitrary as defined by the user.

Right now, the user specifies an optional workflow name, otherwise "default" is used. 

The bot searches for a matching workflow JSON template in the `/workflows` directory and parses it.

The workflow JSON template must be a valid ComfyUI workflow JSON schema. You can get this by going to ComfyUI > Workflow > Export (API).

In the template, you can place the following placeholders, which will get templated with the discord user's input:
- `{{ positive_prompt }}`: The positive prompt input
- `{{ negative_prompt }}`: The negative prompt input
- `{{ model_name }}`: The model name (Defaults to `Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors`)
- `{{ seed }}`: The seed value (Defaults to a random integer if none provided by the user)

See `/workflows/default.json` for an example.

## Usage

### Generate Images:
`/gen_image <prompt> [workflow_name] [negative_prompt] [seed] [model_name] [steps] [cfg] [debug]`

Parameters:
- `prompt` (required): The positive prompt for image generation
- `workflow_name` (optional, default: "default"): Name of the workflow to use from the `/workflows` directory
- `negative_prompt` (optional): Negative prompt to guide what you don't want in the image
- `seed` (optional): Seed value for reproducible results. If not provided, a random seed will be generated
- `model_name` (optional): Name of the model to use for generation
- `steps` (optional): Number of inference steps
- `cfg` (optional): Classifier Free Guidance scale value
- `debug` (optional): When enabled, shows additional technical details in the Discord embed

Features:
- Real-time progress tracking with a visual progress bar
- Concurrent generation prevention (one generation at a time)
- Error handling with informative messages
- Debug mode for detailed generation parameters

The command will use the specified workflow JSON template (or default.json if not specified) and replace the following placeholders with your inputs:
- `{{ positive_prompt }}`: Your main prompt
- `{{ negative_prompt }}`: Your negative prompt
- `{{ model_name }}`: The model name
- `{{ seed }}`: The seed value (random if not provided)
- `{{ steps }}`: Number of inference steps
- `{{ cfg }}`: CFG scale value

### Other commands:
- list models
`/list_models <model_type>`

Queries the ComfyUI API for available models of the specified type.

- list workflows
`/list_workflows`

Lists the available workflows in the `/workflows` directory.

- get system stats
`/get_system_stats`

Queries in the ComfyUI API for system stats.

## License

MIT License
