# Parakeet Dictation for Kubuntu

A local, private, and high-performance dictation tool using the **NVIDIA Parakeet** model. Mimics the Windows "Win+H" experience on Linux.

## Prerequisites

- **NVIDIA GPU** for high-performance dictation.
- **Conda** environment with `torch` and `nemo_toolkit[all]`.
- **System Tools**: `sox` (for recording), `xclip` or `wl-copy` (for clipboard), `xdotool` (for pasting).

## Installation

1. Create and activate the conda environment:
   ```bash
   conda create -n parakeet python=3.11
   conda activate parakeet
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   pip install "nemo_toolkit[all]"
   ```
2. Install system dependencies:
   ```bash
   sudo apt install sox xclip xdotool
   ```
3. Make the script executable:
   ```bash
   chmod +x toggle.sh
   ```

## Kubuntu Setup (Win+H)

1. Open **System Settings** -> **Keyboard** -> **Shortcuts**.
2. Click **Add New** -> **Command or Script**.
3. Name it "Parakeet Dictation".
4. Set the Command to the path of `toggle.sh` in your project folder:
   `/path/to/your/parakeet-dictation/toggle.sh`
5. Assign the shortcut **Meta+H** (or your preferred key).

## Usage

- Press **Win+H** to start recording. A notification will appear.
- Speak clearly.
- Press **Win+H** again to stop. The audio will be processed and automatically typed into your active window.

> [!TIP]
> Ensure your `conda` environment is active when using the script, or edit the `PYTHON_CMD` in `toggle.sh` to point to your environment's python binary.

## Credits

- **NVIDIA NeMo**: [GitHub Repository](https://github.com/NVIDIA/NeMo)
- **Parakeet-TDT 0.6b v3**: [Hugging Face Model Page](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- **Project Blog**: [Turbocharge ASR Accuracy and Speed with NVIDIA NeMo Parakeet-TDT](https://developer.nvidia.com/blog/turbocharge-asr-accuracy-and-speed-with-nvidia-nemo-parakeet-tdt/)
- **Research Paper**: [Canary-1B-v2 & Parakeet-TDT-0.6B-v3](https://arxiv.org/abs/2404.04342)
- **Documentation**: [NVIDIA NeMo ASR Introduction](https://docs.nvidia.com/nemo-toolkit/LATEST/asr/intro.html)

Based on the NVIDIA NeMo Parakeet TDT models.


