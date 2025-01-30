# ComfyUI Discord Bot

A Discord bot for interacting with ComfyUI.

Needs specially crafted workflows using the API-compatible workflow JSON schema, and a matching configuration in config.yaml in order to work.

The bot will attempt to locate these based on name, and then provide the user's user's arguments into the workflow.

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

Copy the config.yaml.template to config.yaml and follow the comments to configure the bot.

## Workflow Configuration

The bot relies on a rather brittle system of using ComfyUI workflows that can be completely arbitrary.

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

### Run prompts:
`/gen_img <poitive_prompt> <optional: negative_prompt> <optional: workflow_name> <optional: debug>`

`positive_prompt` is the only required parameter. It will run the `/workflows/default.json` workflow using this and place the `positive_prmopt` intput into the matching Positive prompt node

`negative_prompt` is optional. If provided, it will place the `negative_prompt` input into the matching Negative prompt node.

`workflow_name` is optional. If provided, it will attempt to load the `/workflows/<workflow_name>.json` file and use that instead of the default workflow.

`debug` is optional. If provided, it will print more information in the resulting embed in discord.

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
