import os
import sys
import wave
import pyaudio
import torch
import torch.utils.data
import subprocess
import logging
import signal
import numpy as np
from scipy import signal as scipy_signal
import nemo.collections.asr as nemo_asr
from threading import Thread, Event
import time
import webrtcvad
import collections

# 1. MONKEY-PATCH for Python 3.13 + Lhotse compatibility
def sampler_init_patch(self, data_source=None):
    pass
torch.utils.data.Sampler.__init__ = sampler_init_patch

# Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
# WebRTCVAD only supports 8000, 16000, 32000, or 48000 Hz
# We'll stick to 16000 for the model
RATE = 16000
# VAD requires 10, 20, or 30ms frames
FRAME_DURATION_MS = 30
CHUNK = int(RATE * FRAME_DURATION_MS / 1000)
WAVE_OUTPUT_FILENAME = "/tmp/voicetype_segment.wav"
LOG_FILENAME = "/tmp/voicetype.log"
MODEL_NAME = "nvidia/parakeet-tdt-0.6b-v3"

logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VoiceTyper:
    def __init__(self):
        logging.info("Initializing Real-Time VoiceTyper...")
        subprocess.run(["notify-send", "Voice Typing", "Initializing model...", "-i", "power-settings"])
        
        try:
            self.asr_model = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained(model_name=MODEL_NAME)
            if hasattr(self.asr_model, 'change_decoding_strategy'):
                self.asr_model.change_decoding_strategy(
                    decoding_cfg={
                        'cuda_graphs': False,
                        'greedy': {'use_cuda_graph_decoder': False},
                        'beam': {'allow_cuda_graphs': False}
                    }
                )
            if torch.cuda.is_available():
                self.asr_model = self.asr_model.cuda()
            self.asr_model.eval()
            logging.info("Model loaded.")
        except Exception as e:
            logging.error(f"Model load failed: {e}", exc_info=True)
            sys.exit(1)
        
        self.vad = webrtcvad.Vad(3) # Aggressiveness 3 (highest)
        self.audio = pyaudio.PyAudio()
        self.stop_event = Event()
        self.transcription_queue = collections.deque()
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logging.info("Stop signal received.")
        self.stop_event.set()

    def record_and_stream(self):
        # Find device
        device_index = None
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            if dev.get('maxInputChannels') > 0 and 'pulse' in dev['name'].lower():
                device_index = i
                break
        
        try:
            stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=device_index, frames_per_buffer=CHUNK)
            logging.info("Stream opened.")
            subprocess.run(["notify-send", "Voice Typing", "Listening... Speak now.", "-i", "mic-on"])

            audio_buffer = []
            triggered = False
            # How many frames of silence before we decide a sentence is finished
            # 30ms * 20 = 600ms
            padding_duration_ms = 600
            num_padding_frames = int(padding_duration_ms / FRAME_DURATION_MS)
            ring_buffer = collections.deque(maxlen=num_padding_frames)
            
            # Transcription thread
            def worker():
                while not self.stop_event.is_set() or self.transcription_queue:
                    if self.transcription_queue:
                        segment = self.transcription_queue.popleft()
                        self.process_segment(segment)
                    else:
                        time.sleep(0.1)
            
            t = Thread(target=worker)
            t.start()

            while not self.stop_event.is_set():
                frame = stream.read(CHUNK, exception_on_overflow=False)
                is_speech = self.vad.is_speech(frame, RATE)

                if not triggered:
                    ring_buffer.append((frame, is_speech))
                    num_voiced = len([f for f, s in ring_buffer if s])
                    if num_voiced > 0.9 * ring_buffer.maxlen:
                        triggered = True
                        for f, s in ring_buffer:
                            audio_buffer.append(f)
                        ring_buffer.clear()
                else:
                    audio_buffer.append(frame)
                    ring_buffer.append((frame, is_speech))
                    num_unvoiced = len([f for f, s in ring_buffer if not s])
                    if num_unvoiced > 0.9 * ring_buffer.maxlen:
                        triggered = False
                        # Segment finished
                        segment_data = b''.join(audio_buffer)
                        self.transcription_queue.append(segment_data)
                        audio_buffer = []
                        ring_buffer.clear()

            stream.stop_stream()
            stream.close()
            t.join()
        except Exception as e:
            logging.error(f"Streaming error: {e}", exc_info=True)

    def process_segment(self, segment_data):
        logging.info("Processing segment...")
        audio_array = np.frombuffer(segment_data, dtype=np.int16)
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS); wf.setsampwidth(2); wf.setframerate(RATE)
        wf.writeframes(audio_array.tobytes()); wf.close()
        
        try:
            text = self._perform_transcription()
            logging.info(f"Transcription result: '{text}'")
            if text and text.strip() and text.strip().lower() != "nan":
                logging.info(f"Typing: {text}")
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                env['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
                # Type text + space
                subprocess.run(["xdotool", "type", "--clearmodifiers", text + " "], env=env)
        except Exception as e:
            logging.error(f"Transcription error: {e}", exc_info=True)

    def _perform_transcription(self):
        """Attempts transcription on GPU, fallbacks to CPU if CUDA graphs or other OOM happens."""
        try:
            with torch.no_grad():
                transcriptions = self.asr_model.transcribe([WAVE_OUTPUT_FILENAME], verbose=False)
                res = transcriptions[0][0] if isinstance(transcriptions[0], list) else transcriptions[0]
                text = res.text if hasattr(res, 'text') else str(res)
                return text
        except Exception as e:
            if "CUDA" in str(e) or "AcceleratorError" in str(e) or "INTERNAL ASSERT" in str(e):
                logging.warning(f"GPU transcription failed: {e}. Falling back to CPU...")
                try:
                    self.asr_model = self.asr_model.cpu()
                    with torch.no_grad():
                        transcriptions = self.asr_model.transcribe([WAVE_OUTPUT_FILENAME], verbose=False)
                        res = transcriptions[0][0] if isinstance(transcriptions[0], list) else transcriptions[0]
                        return res.text if hasattr(res, 'text') else str(res)
                except Exception as e2:
                    logging.error(f"CPU fallback also failed: {e2}")
                    raise e2
            else:
                raise e

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    typer = VoiceTyper()
    typer.record_and_stream()
    logging.info("Exited.")
