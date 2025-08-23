"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pydantic import BaseModel
from typing import List, Optional


class ImageData(BaseModel):
    """Model for image data with hash identifier.

    Attributes:
        serialized_image: Optional Base64 encoded string of the image content.
        mime_type: MIME type of the image.
    """

    serialized_image: str
    mime_type: str


class ChatRequest(BaseModel):
    """Model for a chat request.

    Attributes:
        text: The text content of the message.
        files: List of image data objects
        session_id: Session identifier for the conversation.
        user_id: User identifier for the conversation.
    """

    text: str
    files: List[ImageData] = []
    session_id: str = "default_session"
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    """Model for a chat response.

    Attributes:
        response: The text response from the model.
        thinking_process: Optional thinking process of the model.
        attachments: List of image data to be displayed to the user.
        error: Optional error message if something went wrong.
    """

    response: str
    thinking_process: str = ""
    attachments: List[ImageData] = []
    error: Optional[str] = None
