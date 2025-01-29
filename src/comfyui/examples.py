import asyncio
import json
import logging
from pathlib import Path
from client import ComfyUIClient

logging.basicConfig(level=logging.INFO)

async def simple_example():
    """
    A simple example showing how to connect to ComfyUI and track a prompt's execution.
    """
    client = ComfyUIClient()
    
    try:
        # Connect to ComfyUI
        await client.connect()
        
        # Load a workflow file (you'll need to create this)
        workflow_path = Path("workflows/basic_workflow.json")
        with open(workflow_path) as f:
            workflow = json.load(f)
        
        # Queue the prompt
        response = await client.queue_prompt(workflow)
        prompt_id = response["prompt_id"]
        print(f"Queued prompt with ID: {prompt_id}")
        
        # Track the execution progress
        await client.track_progress(prompt_id)
        
        # Get the execution history
        history = await client.get_history(prompt_id)
        print(f"Execution history: {json.dumps(history, indent=2)}")
        
    finally:
        # Always close the connection
        await client.close()

if __name__ == "__main__":
    asyncio.run(simple_example())