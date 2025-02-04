"""
Model for handling ComfyUI workflows JSON.
"""
from pathlib import Path
import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from .workflow_template import WorkflowTemplate


# Configure logging
logger = logging.getLogger(__name__)

class WorkflowJson:
    """
    Model for handling ComfyUI workflows JSON in API format.

    Validates the template exists, then passes context off to WorkflowTemplate which does the actual rendering.

    Has some other helper methods for extracting information from the workflow.

    Returns the templated JSON, ready to be submitted to the ComfyUI API.
    """
    def __init__(self, workflow_name: str, model_name: Optional[str] = None):
        self.workflow_name = workflow_name

        self.template = self._load_workflow()
    
    def _load_workflow(self) -> WorkflowTemplate:
        """
            Find and load the workflow template, or throw an exception.
        """
        workflow_path = None
        workflows_dir = Path("src/discord_comfyui/templates")
        for file in workflows_dir.glob("*.json"):
            if file.stem == self.workflow_name:
                workflow_path = file
                break
        
        if not workflow_path:
            raise ValueError(f"Workflow '{self.workflow_name}' not found")
            
        return WorkflowTemplate(f"{self.workflow_name}.json")
    
    def get_node_descriptions(self) -> List[str]:
        """Extract descriptions of nodes in the workflow"""
        # Get the workflow data first
        workflow_data = self.get_workflow_data()
        
        descriptions = []
        for node_id, node_info in workflow_data.items():
            descriptions.append(
                f"Node {node_id}: {node_info['class_type']} - {node_info.get('_meta', {}).get('title')}"
            )
        return descriptions

    def get_model_name(self) -> str:
        """Get the model name from the workflow"""
        return self.model_name
    
    def get_workflow_api_json(self, context: Dict) -> Dict[str, Any]:
        """
        Render the actual workflow JSON with the provided context using Jinja
        """
        rendered_json = self.template.render(context)
        
        # Save the rendered JSON to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = Path("saved") / f"{self.workflow_name}_{timestamp}.json"
        
        with open(save_path, 'w') as f:
            json.dump(rendered_json, f, indent=2)
            logger.info(f"Rendered workflow JSON saved to {save_path}")
            
        return rendered_json
