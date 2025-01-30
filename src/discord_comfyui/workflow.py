import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from .workflow_template import WorkflowTemplate, WorkflowTemplateConfig

class Workflow:
    """
    Model for handling ComfyUI workflows JSON.

    Interacts with a WorkloadTemplate which defines what to template into the workflow JSON and where.
    This WorkloadTemplate is defined in the config.yaml
    
    """
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.workflow_json: Optional[Dict[str, Any]] = None
        self.template: Optional[WorkflowTemplate] = None
        self._load_workflow()
        self._init_template()
    
    def _load_workflow(self) -> None:
        """Find and load the workflow file"""
        workflow_path = None
        workflows_dir = Path("workflows")
        for file in workflows_dir.glob("*.json"):
            if file.stem == self.workflow_name:
                workflow_path = file
                break
        
        if not workflow_path:
            raise ValueError(f"Workflow '{self.workflow_name}' not found")
        
        # Load and parse the workflow JSON
        with open(workflow_path) as f:
            self.workflow_json = json.load(f)
    
    def _load_template_config(self) -> WorkflowTemplateConfig:
        """Load the template configuration from config.yaml"""
        with open("config.yaml") as f:
            config = yaml.safe_load(f)
        
        # Get the default template configuration
        template_config = config.get("workflows", {}).get("templates", {}).get(self.workflow_name)
        if not template_config:
            raise ValueError(f"Config for workflow {self.workflow_name} not found in config.yaml")
        
        return WorkflowTemplateConfig.from_dict(template_config)
    
    def _init_template(self) -> None:
        """Initialize the workflow template"""
        if not self.workflow_json:
            return
            
        template_config = self._load_template_config()
        self.template = WorkflowTemplate(self.workflow_json, template_config)
    
    def update_prompts(self, positive_prompt: str, negative_prompt: Optional[str] = None) -> None:
        """Update the positive and negative prompts in the workflow"""
        if not self.template:
            return
            
        prompts = {"positive": positive_prompt}
        if negative_prompt:
            prompts["negative"] = negative_prompt
            
        self.template.update_prompts(prompts)
    
    def get_node_descriptions(self) -> List[str]:
        """Extract descriptions of nodes in the workflow"""
        if not self.workflow_json:
            return []
            
        descriptions = []
        for node_id, node_info in self.workflow_json.items():
            descriptions.append(
                f"Node {node_id}: {node_info['class_type']} - {node_info.get('_meta', {}).get('title')}"
            )
        return descriptions

    def get_model_name(self) -> str:
        """Get the model name from the workflow"""
        if not self.template:
            return ""
            
        return self.template.get_model_name()
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get the workflow data"""
        if not self.template:
            raise ValueError("Workflow template not initialized")
            
        return self.template.get_workflow_data()
