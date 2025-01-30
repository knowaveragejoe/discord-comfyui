"""
Workflow model for handling ComfyUI workflow operations
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

class Workflow:
    """Model for handling ComfyUI workflows"""
    def __init__(self, workflow_name: str):
        self.workflow_name = workflow_name
        self.workflow_json: Optional[Dict[str, Any]] = None
        self._load_workflow()
    
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
    
    def update_prompts(self, positive_prompt: str, negative_prompt: Optional[str] = None) -> None:
        """Update the positive and negative prompts in the workflow"""
        if not self.workflow_json:
            return
            
        for node_id, node_info in self.workflow_json.items():
            if "_meta" in node_info and "title" in node_info["_meta"]:
                title = node_info["_meta"]["title"]
                if "Positive" in title and "inputs" in node_info:
                    node_info["inputs"]["text"] = positive_prompt
                elif "Negative" in title and "inputs" in node_info and negative_prompt:
                    node_info["inputs"]["text"] = negative_prompt
    
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
        """Extract the model name from the workflow by finding the first CheckpointLoaderSimple node"""
        if not self.workflow_json:
            return ""
        
        for node_id, node_info in self.workflow_json.items():
            if node_info.get("class_type") == "CheckpointLoaderSimple":
                return node_info.get("inputs", {}).get("ckpt_name", "")
        
        return ""
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get the workflow data"""
        if not self.workflow_json:
            raise ValueError("Workflow not loaded")
        return self.workflow_json
