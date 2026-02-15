import torch
import os
from huggingface_hub import snapshot_download

print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.get_device_name(0)}")

MODEL_ID = "nvidia/parakeet-tdt-0.6b-v3"
print(f"Attempting to download/verify {MODEL_ID}...")

# This will download the model or use the cache if already present
# NeMo usually looks in ~/.cache/torch/NeMo/
# But snapshot_download is more explicit for debugging
try:
    path = snapshot_download(repo_id=MODEL_ID, repo_type="model")
    print(f"Model downloaded to: {path}")
except Exception as e:
    print(f"Download failed: {e}")
