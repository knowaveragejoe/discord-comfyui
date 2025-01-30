"""
Module for handling ComfyUI workflow templates and configuration
"""
from typing import Dict, Any
from pathlib import Path
import json
from jinja2 import Template

class WorkflowTemplate:
    """Handles workflow template processing using Jinja2"""
    
    def __init__(self, template_path: str):
        """Initialize with path to workflow template file"""
        self.template_path = template_path
        with open(template_path, 'r') as f:
            self.template_str = f.read()
            
    def render(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render the workflow template with the provided context
        
        Args:
            context: Dictionary containing template variables:
                - user_prompt: The positive prompt text
                - user_negative_prompt: The negative prompt text (optional)
                - model_name: Name of the model checkpoint to use
                
        Returns:
            Dict containing the rendered workflow data
        """
        template = Template(self.template_str)
        rendered = template.render(**context)
        return json.loads(rendered)
    
    def render_template(self, context: Dict) -> Dict[str, Any]:
        """
        Get the processed workflow data with the given parameters
        """
        return self.render(context)
