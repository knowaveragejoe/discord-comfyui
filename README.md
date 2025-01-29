# ComfyUI Discord Bot

A Discord bot for interacting with ComfyUI.

Needs specially crafted workflows using the API-compatible workflow JSON schema.

On the ComfyUI server, these can be placed in the `/workflows` directory.
The bot will attempt to locate these based on name, and then provide the user's prompt argument into the workflow.

## Commands
- run prompts
`/gen_img <workflow_name> <prompt>`
- list models
`/list_models <model_type>`
- list workflows
`/list_workflows`
- get system stats
`/get_system_stats`

## Setup

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

## Configuration

Copy the config.yaml.template to config.yaml and follow the comments to configure the bot.

## Development

This project uses modern Python tooling:

- `pyproject.toml` for project metadata and dependencies
- `uv` for dependency management and virtual environments
- Type hints and modern Python features (requires Python 3.10+)

## License

MIT License
