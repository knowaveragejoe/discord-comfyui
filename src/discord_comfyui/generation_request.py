"""
Generation request model for handling workflow processing
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any

class GenerationRequest:
    """Model for handling image generation requests"""
    def __init__(
        self,
        prompt: str,
        workflow_name: str,
        negative_prompt: Optional[str] = None,
        prompt_id: Optional[str] = None
    ):
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.prompt_id = prompt_id
        self.workflow_name = workflow_name
        self.workflow_json: Optional[Dict[str, Any]] = None
        
        # Process the workflow immediately upon initialization
        self._process_workflow()
    
    def _process_workflow(self) -> None:
        """Find, load and process the workflow file"""
        # Find the workflow file
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
        
        # Update prompt nodes
        for node_id, node_info in self.workflow_json.items():
            if "_meta" in node_info and "title" in node_info["_meta"]:
                title = node_info["_meta"]["title"]
                if "Positive" in title and "inputs" in node_info:
                    node_info["inputs"]["text"] = self.prompt
                elif "Negative" in title and "inputs" in node_info and self.negative_prompt:
                    node_info["inputs"]["text"] = self.negative_prompt
    
    def get_node_descriptions(self) -> list[str]:
        """Extract descriptions of nodes in the workflow"""
        if not self.workflow_json:
            return []
            
        descriptions = []
        for node_id, node_info in self.workflow_json.items():
            descriptions.append(
                f"Node {node_id}: {node_info['class_type']} - {node_info.get('_meta', {}).get('title')}"
            )
        return descriptions
