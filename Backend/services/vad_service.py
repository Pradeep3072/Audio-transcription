import torch
import numpy as np

TARGET_SAMPLE_RATE = 16000
VAD_CHUNK_SIZE = 512


class VADService:

    def __init__(self):

        print("Loading Silero VAD...")

        self.model, self.utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            trust_repo=True
        )

        print("Silero VAD loaded!")

        # Audio buffer
        self.buffer = np.array(
            [],
            dtype=np.float32
        )


    def process_audio(
        self,
        audio: np.ndarray,
        sample_rate: int
    ):

        # =====================================
        # Convert stereo → mono
        # =====================================

        if audio.ndim > 1:
            audio = np.mean(
                audio,
                axis=0
            )
        else:
            audio = audio.flatten()


        # =====================================
        # Convert to float32
        # =====================================

        audio = audio.astype(
            np.float32
        )


        # =====================================
        # Normalize audio properly
        # =====================================

        if np.max(np.abs(audio)) > 1.0:
            audio = audio / 32768.0


        # =====================================
        # Add to raw buffer
        # =====================================

        if getattr(self, 'raw_buffer', None) is None:
            self.raw_buffer = np.array([], dtype=np.float32)

        self.raw_buffer = np.concatenate([self.raw_buffer, audio])

        results = []

        # =====================================
        # Calculate samples needed for 512 at 16kHz
        # =====================================
        
        required_raw_samples = int(VAD_CHUNK_SIZE * sample_rate / TARGET_SAMPLE_RATE)

        while len(self.raw_buffer) >= required_raw_samples:
            
            raw_chunk = self.raw_buffer[:required_raw_samples]
            self.raw_buffer = self.raw_buffer[required_raw_samples:]

            # =================================
            # Resample chunk using Decimation
            # =================================

            if sample_rate != TARGET_SAMPLE_RATE:
                step = sample_rate // TARGET_SAMPLE_RATE
                chunk_16k = raw_chunk[::step].astype(np.float32)
            else:
                chunk_16k = raw_chunk
                
            # Ensure exact chunk size (pad or trim due to polyphase length)
            if len(chunk_16k) > VAD_CHUNK_SIZE:
                chunk_16k = chunk_16k[:VAD_CHUNK_SIZE]
            elif len(chunk_16k) < VAD_CHUNK_SIZE:
                chunk_16k = np.pad(chunk_16k, (0, VAD_CHUNK_SIZE - len(chunk_16k)))

            # =================================
            # Convert to Tensor
            # =================================

            tensor = torch.from_numpy(chunk_16k)

            # =================================
            # Silero VAD
            # =================================

            speech_probability = self.model(
                tensor,
                TARGET_SAMPLE_RATE
            ).item()

            speech_detected = (
                speech_probability > 0.5
            )

            results.append(
                (
                    speech_probability,
                    speech_detected
                )
            )

        return results