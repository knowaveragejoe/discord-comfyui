"""
Generation request model for handling workflow processing
"""
from typing import Optional, Dict, Any, List
from .workflow import Workflow

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
        self.workflow = Workflow(workflow_name)
        
        # Update prompts in the workflow
        self.workflow.update_prompts(self.prompt, self.negative_prompt)
    
    def get_node_descriptions(self) -> List[str]:
        """Extract descriptions of nodes in the workflow"""
        return self.workflow.get_node_descriptions()

    def get_model_name(self) -> str:
        """Extract the model name from the workflow"""
        return self.workflow.get_model_name()
    
    def get_workflow_data(self) -> Dict[str, Any]:
        """Get the workflow data"""
        return self.workflow.get_workflow_data()
