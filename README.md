# ComfyUI Discord Bot

A Discord bot for interacting with ComfyUI, allowing users to generate images through Discord commands.

## Setup

1. Create a virtual environment and install the bot:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On Unix systems
   # OR
   .venv\Scripts\activate  # On Windows
   
   uv pip install -e .
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with your Discord bot token and ComfyUI server details.

4. Run the bot:
   ```bash
   comfyui-discord-bot
   ```

## Configuration

The following environment variables need to be set in your `.env` file:

- `DISCORD_TOKEN`: Your Discord bot token
- `DISCORD_GUILD_ID`: The ID of your Discord server
- `COMFYUI_HOST`: The hostname of your ComfyUI server (default: 127.0.0.1)
- `COMFYUI_PORT`: The port of your ComfyUI server (default: 8188)

## Development

This project uses modern Python tooling:

- `pyproject.toml` for project metadata and dependencies
- `uv` for dependency management and virtual environments
- Type hints and modern Python features (requires Python 3.10+)

## License

MIT License
