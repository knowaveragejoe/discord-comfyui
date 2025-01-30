"""
Command implementations for the ComfyUI Discord bot
"""

from .system_stats import SystemStatsCommand
from .list_models import ListModelsCommand
from .list_workflows import ListWorkflowsCommand
from .generate_image import GenerateImageCommand
from .gif import GifCommand

# List of all command classes for easy registration
COMMANDS = [
    SystemStatsCommand,
    ListModelsCommand,
    ListWorkflowsCommand,
    GenerateImageCommand,
    GifCommand
]

__all__ = [
    'SystemStatsCommand',
    'ListModelsCommand',
    'ListWorkflowsCommand',
    'GenerateImageCommand',
    'GifCommand',
    'COMMANDS'
]
