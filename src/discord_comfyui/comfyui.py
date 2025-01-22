import asyncio
import json
import logging
import uuid
from typing import Optional, Dict, Any, Callable
import urllib.request
import urllib.parse
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)

class ComfyUIClient:
    """
    A client for interacting with ComfyUI's WebSocket API.
    
    This client handles WebSocket communication with ComfyUI, including:
    - Establishing and maintaining WebSocket connections
    - Sending prompts and tracking their execution
    - Receiving real-time updates on prompt execution progress
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        """
        Initialize the ComfyUI client.
        
        Args:
            host: The hostname where ComfyUI is running
            port: The port number ComfyUI is listening on
        """
        self.server_address = f"{host}:{port}"
        self.client_id = str(uuid.uuid4())
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.base_url = f"http://{self.server_address}"
        self.ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"
        
    async def connect(self) -> None:
        """Establish a WebSocket connection to ComfyUI."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            logger.info(f"Connected to ComfyUI at {self.ws_url}")
            # Receive the initial status message
            initial_msg = await self.websocket.recv()
            logger.debug(f"Received initial status: {initial_msg}")
        except Exception as e:
            logger.error(f"Failed to connect to ComfyUI: {e}")
            raise

    async def queue_prompt(self, prompt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queue a prompt for execution in ComfyUI.
        
        Args:
            prompt: The workflow prompt to execute
            
        Returns:
            Dict containing the prompt_id and other response data
        """
        data = {
            "prompt": prompt,
            "client_id": self.client_id
        }
        headers = {'Content-Type': 'application/json'}
        encoded_data = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=encoded_data,
            headers=headers
        )
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read())

    async def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get the execution history for a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt to get history for
            
        Returns:
            Dict containing the prompt execution history
        """
        url = f"{self.base_url}/history/{prompt_id}"
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())

    async def get_image(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """
        Retrieve an image from ComfyUI.
        
        Args:
            filename: Name of the image file
            subfolder: Subfolder containing the image
            folder_type: Type of folder ("input", "output", or "temp")
            
        Returns:
            Raw image data as bytes
        """
        params = {
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        }
        url_values = urllib.parse.urlencode(params)
        url = f"{self.base_url}/view?{url_values}"
        
        with urllib.request.urlopen(url) as response:
            return response.read()

    async def track_progress(self, prompt_id: str, callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> None:
        """
        Track the progress of a prompt execution.
        
        Args:
            prompt_id: The ID of the prompt to track
            callback: Optional callback function to handle progress updates
        """
        if not self.websocket:
            raise RuntimeError("Not connected to ComfyUI. Call connect() first.")

        try:
            while True:
                message = await self.websocket.recv()
                if isinstance(message, str):
                    data = json.loads(message)
                    
                    # Call the callback if provided
                    if callback:
                        callback(data)
                    
                    # Log progress information
                    if data["type"] == "progress":
                        progress_data = data["data"]
                        logger.info(f"Progress: {progress_data['value']}/{progress_data['max']}")
                    
                    # Check if execution is complete
                    elif data["type"] == "executing":
                        if data["data"]["node"] is None and data["data"]["prompt_id"] == prompt_id:
                            logger.info("Execution completed")
                            break
        except Exception as e:
            logger.error(f"Error while tracking progress: {e}")
            raise

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from ComfyUI")