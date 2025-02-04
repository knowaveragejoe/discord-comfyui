import asyncio
import json
import logging
import struct
import uuid
from typing import Optional, Dict, Any, Callable
import aiohttp
import httpx
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)

class BinaryEventTypes:
    PREVIEW_IMAGE = 1

model_types = [
    "checkpoints",
    "clip_vision",
    "controlnet",
    "diffusion_models",
    "gligen",
    "loras",
    "style_models",
    "unet",
    "vae",
    "clip",
    "configs",
    "diffusers",
    "embeddings",
    "hypernetworks",
    "photomaker",
    "text_encoders",
    "upscale_models",
    "vae_approx",
]

class ComfyUIClient:
    """
    A client for interacting with ComfyUI's WebSocket API.
    
    This client handles WebSocket communication with ComfyUI, including:
    - Establishing and maintaining WebSocket connections
    - Sending prompts and tracking their execution
    - Receiving real-time updates on prompt execution progress
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = None):
        """
        Initialize the ComfyUI client.
        
        Args:
            host: The hostname where ComfyUI is running
            port: The port number ComfyUI is listening on
        """
        self.server_address = host
        if port:
            self.server_address = f"{host}:{port}"
        self.client_id = str(uuid.uuid4())
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.http_client = httpx.AsyncClient()
        self.base_url = f"https://{self.server_address}"
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

    async def list_models(self, model_type: str = "checkpoints") -> Dict[str, Any]:
        """
        List available models from ComfyUI.
        
        Returns:
            Dict containing available models and their types
        """
        url = f"{self.base_url}/models/{model_type}"
        logger.info(f"Listing models of type: {model_type}")
        logger.info(f"GET {url}")

        response = await self.http_client.get(url)
        response.raise_for_status()
        return response.json()

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
        
        response = await self.http_client.post(
            f"{self.base_url}/prompt",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics from ComfyUI.
        
        Returns:
            Dict containing system statistics like memory usage, device info, etc.
        """
        response = await self.http_client.get(f"{self.base_url}/system_stats")
        response.raise_for_status()
        return response.json()

    async def get_history(self) -> Dict[str, Any]:
        """
        Get the execution history for all prompts.
        
        Returns:
            Dict containing the prompt execution history
        """
        response = await self.http_client.get(f"{self.base_url}/history")
        response.raise_for_status()
        return response.json()

    async def get_history_for_prompt(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get the execution history for a specific prompt.
        
        Args:
            prompt_id: The ID of the prompt to get history for
            
        Returns:
            Dict containing the prompt execution history
        """
        response = await self.http_client.get(f"{self.base_url}/history/{prompt_id}")
        response.raise_for_status()
        return response.json()

    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "") -> bytes:
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
        
        response = await self.http_client.get(f"{self.base_url}/view", params=params)
        response.raise_for_status()
        return response.content

    def extract_filename(self, data: Dict[str, Any]) -> str:
        """Extract the output image filename from execution data with proper error handling.
        
        Args:
            data: The execution data dictionary from ComfyUI
            
        Returns:
            The extracted filename or empty string if not found/invalid
        """
        try:
            return data["data"]["output"]["images"][0]["filename"]
        except (KeyError, IndexError, TypeError):
            logger.warning("Could not extract filename from execution data")
            return ""

    async def track_progress(self, prompt_id: str, callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> str:
        """
        Track the progress of a prompt execution.
        
        Args:
            prompt_id: The ID of the prompt to track
            callback: Optional callback function to handle progress updates
        """
        if not self.websocket:
            raise RuntimeError("Not connected to ComfyUI. Call connect() first.")


        image_filename = ""
        try:
            while True:
                message = await self.websocket.recv()
                if isinstance(message, str):
                    data = json.loads(message)
                    # logger.info(f"Received message: {data}")
                    
                    # Call the callback if provided
                    if callback:
                        await callback(data)
                    
                    # Log progress information
                    if data["type"] == "progress":
                        pass
                        # progress_data = data["data"]
                        # logger.info(f"Progress: {progress_data['value']}/{progress_data['max']}")
                    
                    # technically we are "done" here, but we need to wait for the last "executing" message"
                    # store the output filename for later retrieval.
                    elif data["type"] == "executed":
                        image_filename = self.extract_filename(data)
                            
                    
                    # execution is "actually" finished here, so this is where we break
                    elif data["type"] == "executing":
                        if data["data"]["node"] is None and data["data"]["prompt_id"] == prompt_id:
                            logger.info("Execution completed")
                            break
                else:
                    if isinstance(message, bytes):
                        # First 4 bytes are the event type
                        event_type = struct.unpack(">I", message[:4])[0]
                        
                        if event_type == BinaryEventTypes.PREVIEW_IMAGE:
                            # Next 4 bytes are the image format
                            image_format = struct.unpack(">I", message[4:8])[0]
                            # Remaining data is the image bytes
                            image_data = message[8:]
                            
                            format_name = "JPEG" if image_format == 1 else "PNG"
                            logger.info(f"Received preview image in {format_name} format")
                            # TODO: Handle the preview image data as needed

                            if callback:
                                await callback({
                                    "type": "preview_image",
                                    "data": {
                                        "format": format_name,
                                        "image_data": image_data
                                    }
                                })
                    
                    else:
                        logger.warning(f"Unexpected message type: {type(message)}")
        except Exception as e:
            logger.error(f"Error while tracking progress: {e}")
            raise

        return image_filename

    async def close(self) -> None:
        """Close the WebSocket and HTTP connections."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from ComfyUI")
        
        await self.http_client.aclose()
        logger.info("Closed HTTP client")
