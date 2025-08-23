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

from datasets import load_dataset
import os

# Using mousserlane/id_receipt_dataset dataset
ds = load_dataset("mousserlane/id_receipt_dataset")

# Directory to save images
output_dir = "receipt_samples"
os.makedirs(output_dir, exist_ok=True)

for idx, item in enumerate(ds["train"]):
    image = item["image"]
    # The image is a PIL Image object; save it as a PNG file
    image_path = os.path.join(output_dir, f"{idx}.png")
    image.save(image_path)

print("All images have been saved to the receipt_samples directory.")
