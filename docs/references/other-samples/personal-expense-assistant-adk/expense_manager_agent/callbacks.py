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

import hashlib
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest


def modify_image_data_in_history(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    # The following code will modify the request sent to LLM
    # We will only keep image data in the last 3 user messages using a reverse and counter approach

    # Count how many user messages we've processed
    user_message_count = 0

    # Process the reversed list
    for content in reversed(llm_request.contents):
        # Only count for user manual query, not function call
        if (content.role == "user") and (content.parts[0].function_response is None):
            user_message_count += 1
            modified_content_parts = []

            # Check any missing image ID placeholder for any image data
            # Then remove image data from conversation history if more than 3 user messages
            for idx, part in enumerate(content.parts):
                if part.inline_data is None:
                    modified_content_parts.append(part)
                    continue

                if (
                    (idx + 1 >= len(content.parts))
                    or (content.parts[idx + 1].text is None)
                    or (not content.parts[idx + 1].text.startswith("[IMAGE-ID "))
                ):
                    # Generate hash ID for the image and add a placeholder
                    image_data = part.inline_data.data
                    hasher = hashlib.sha256(image_data)
                    image_hash_id = hasher.hexdigest()[:12]
                    placeholder = f"[IMAGE-ID {image_hash_id}]"

                    # Only keep image data in the last 3 user messages
                    if user_message_count <= 3:
                        modified_content_parts.append(part)

                    modified_content_parts.append(types.Part(text=placeholder))

                else:
                    # Only keep image data in the last 3 user messages
                    if user_message_count <= 3:
                        modified_content_parts.append(part)

            # This will modify the contents inside the llm_request
            content.parts = modified_content_parts
