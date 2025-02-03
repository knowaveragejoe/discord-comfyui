"""
Generation request model for handling workflow processing
"""
from typing import Optional, Dict, Any, List
from .workflow_json import WorkflowJson

class GenerationRequest:
    """Model for handling image generation requests"""
    def __init__(
        self,
        prompt: str,
        workflow_name: str,
        negative_prompt: Optional[str] = None,
        model_name: Optional[str] = None,
        seed: Optional[str] = None,
        prompt_id: Optional[str] = None,
        steps: Optional[int] = None,
        cfg: Optional[float] = None
    ):
        """
        GenerationRequest mediates between user inputs and rendering ComfyUI API-compatible workflow JSOn.

        This is where default values for the ComfyUI API Prompt request are set.
        
        Args:
            prompt: The positive prompt text
            workflow_name: Name of the workflow template to use
            negative_prompt: Optional negative prompt text
            prompt_id: Optional ID for tracking the generation progress
        """
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.seed = seed
        self.model_name = model_name or "flux1-dev-fp8.safetensors"
        #"Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors"  # Default model
        self.prompt_id = prompt_id
        self.steps = steps or 20  # Default to 20 steps
        self.cfg = cfg or 7  # Default to 7.0 CFG
        self.workflow = WorkflowJson(workflow_name)         
    
    def set_prompt_id(self, prompt_id: str) -> None:
        """Set the prompt ID ComfyUI gives us for tracking the generation progress"""
        self.prompt_id = prompt_id

    def get_node_descriptions(self) -> List[str]:
        """Extract descriptions of nodes in the workflow"""
        return self.workflow.get_node_descriptions()

    def get_model_name(self) -> str:
        """Extract the model name from the workflow"""
        return self.model_name
    
    def get_workflow_api_json(self) -> Dict[str, Any]:
        """Get the processed workflow JSON for the ComfyUI API"""
        context = {
            "positive_prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "model_name": self.model_name,
            "seed": self.seed,
            "steps": self.steps,
            "cfg": self.cfg
        }

        return self.workflow.get_workflow_api_json(context)
