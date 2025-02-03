"""
Module for handling ComfyUI workflow templates and configuration
"""
from typing import Dict, Any, Union
from pathlib import Path
import json
from jinja2 import Template, Environment, BaseLoader

def to_int(value: Union[str, int, None]) -> int:
    """Convert value to integer, with None handling"""
    if value is None:
        return 0
    return int(value)

def to_float(value: Union[str, float, None]) -> float:
    """Convert value to float, with None handling"""
    if value is None:
        return 0.0
    return float(value)

class WorkflowTemplate:
    """Handles workflow template processing using Jinja2"""
    
    def __init__(self, template_path: str):
        """Initialize with path to workflow template file"""
        self.template_path = template_path
        # Create Jinja environment with custom filters
        self.env = Environment(loader=BaseLoader())
        self.env.filters['toint'] = to_int
        self.env.filters['tofloat'] = to_float
        
        # Load template content
        with open(template_path, 'r') as f:
            self.template_str = f.read()
            
    def render(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the workflow template with the provided context
        
        Args:
            context: Dictionary containing template variables:
                - positive_prompt: The positive prompt text
                - negative_prompt: The negative prompt text (optional)
                - model_name: Name of the model checkpoint to use
                - seed: Random seed for generation
                - steps: Number of sampling steps (integer)
                - cfg: Classifier free guidance scale (float)
                
        Returns:
            Dict containing the rendered workflow data
        """
        # Create template from environment to use custom filters
        template = self.env.from_string(self.template_str)
        
        # Render template first, then parse as JSON
        rendered = template.render(**context)
        return json.loads(rendered)
