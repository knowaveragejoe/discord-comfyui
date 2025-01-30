"""
Module for handling ComfyUI workflow templates and configuration
"""
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import json
from jinja2 import Template
from dataclasses import dataclass

@dataclass
class NodeTemplate:
    """Configuration for a node template in the workflow"""
    node_type: str
    path: List[str]
    match_meta: Optional[str] = None

@dataclass
class WorkflowTemplateConfig:
    """Configuration for a workflow template"""
    model: NodeTemplate
    prompts: Dict[str, NodeTemplate]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowTemplateConfig':
        """Create a WorkflowTemplateConfig from a dictionary"""
        model = NodeTemplate(
            node_type=data["model"]["node_type"],
            path=data["model"]["path"],
            match_meta=data["model"].get("match_meta")
        )
        
        prompts = {}
        for name, prompt_data in data["prompts"].items():
            prompts[name] = NodeTemplate(
                node_type=prompt_data["node_type"],
                path=prompt_data["path"],
                match_meta=prompt_data.get("match_meta")
            )
        
        return cls(model=model, prompts=prompts)

class WorkflowTemplate:
    """Handles workflow template processing and validation"""
    
    def __init__(self, workflow_data: Dict[str, Any], template_config: WorkflowTemplateConfig):
        self.workflow_data = workflow_data
        self.template_config = template_config
        self._validate_workflow()
    
    def _validate_workflow(self) -> None:
        """Validate that the workflow contains the required nodes"""
        # Validate model node exists
        model_found = False
        for node in self.workflow_data.values():
            if node.get("class_type") == self.template_config.model.node_type:
                model_found = True
                break
        if not model_found:
            raise ValueError(f"Workflow missing required model node of type {self.template_config.model.node_type}")
        
        # Validate prompt nodes exist
        for prompt_name, prompt_config in self.template_config.prompts.items():
            prompt_found = False
            for node in self.workflow_data.values():
                if node.get("class_type") == prompt_config.node_type:
                    if prompt_config.match_meta:
                        # Check meta title if specified
                        if prompt_config.match_meta in node.get("_meta", {}).get("title", ""):
                            prompt_found = True
                            break
                    else:
                        prompt_found = True
                        break
            if not prompt_found:
                raise ValueError(f"Workflow missing required prompt node '{prompt_name}' of type {prompt_config.node_type}")
    
    def _get_node_value(self, node: Dict[str, Any], path: List[str]) -> Any:
        """Get a value from a node following the given path"""
        current = node
        for key in path:
            if key not in current:
                raise ValueError(f"Invalid path {path} for node")
            current = current[key]
        return current
    
    def _set_node_value(self, node: Dict[str, Any], path: List[str], value: Any) -> None:
        """Set a value in a node following the given path"""
        current = node
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value
    
    def get_model_name(self) -> str:
        """Get the model name from the workflow"""
        for node in self.workflow_data.values():
            if node.get("class_type") == self.template_config.model.node_type:
                return self._get_node_value(node, self.template_config.model.path)
        return ""
    
    def update_prompts(self, prompts: Dict[str, str]) -> None:
        """Update prompts in the workflow
        
        Args:
            prompts: Dictionary mapping prompt names to values
        """
        for prompt_name, prompt_value in prompts.items():
            if prompt_name not in self.template_config.prompts:
                continue
                
            prompt_config = self.template_config.prompts[prompt_name]
            for node in self.workflow_data.values():
                if node.get("class_type") != prompt_config.node_type:
                    continue
                    
                if prompt_config.match_meta:
                    # Check meta title if specified
                    if prompt_config.match_meta not in node.get("_meta", {}).get("title", ""):
                        continue
                
                # Update the prompt value
                self._set_node_value(node, prompt_config.path, prompt_value)
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get the processed workflow data"""
        return self.workflow_data
