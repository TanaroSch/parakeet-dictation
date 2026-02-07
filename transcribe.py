#!/usr/bin/env python3
import argparse
import os
import sys

# Silent NeMo/PyTorch/etc logs for cleaner output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def transcribe(input_file):
    try:
        import torch
        import nemo.collections.asr as nemo_asr
    except ImportError:
        print("Error: nemo_toolkit or torch is not installed.")
        print("Please install them using: pip install torch nemo_toolkit[all]")
        sys.exit(1)

    # Use the official pretrained model name from Hugging Face
    model_name = "nvidia/parakeet-tdt-0.6b-v3"

    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}")
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        # Load the model from the official registry (it will download if not cached)
        model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name, map_location=device)
        model = model.to(device)
        model.eval()

        # Transcribe
        transcriptions = model.transcribe([input_file], verbose=False)
        
        # Handle different return formats from transcribe
        if isinstance(transcriptions, tuple):
            transcriptions = transcriptions[0]
            
        if transcriptions and len(transcriptions) > 0:
            # Print ONLY the transcription to stdout for easy piping in shell scripts
            print(transcriptions[0].strip())
        else:
            sys.exit(0)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe an audio file using NVIDIA Parakeet.")
    parser.add_argument("--input", required=True, help="Path to the input audio file.")
    args = parser.parse_args()

    transcribe(args.input)
