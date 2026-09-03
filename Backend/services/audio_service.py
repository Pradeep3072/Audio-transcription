import io
import wave

import numpy as np
from scipy.signal import resample


TARGET_SAMPLE_RATE = 16000


def create_wav(audio_frames, original_sample_rate):

    # Combine frames
    audio = np.concatenate(
        audio_frames,
        axis=1
    )

    # --------------------------------
    # Convert to mono
    # --------------------------------

    if audio.shape[0] > 1:

        audio = np.mean(
            audio,
            axis=0
        )

    else:

        audio = audio[0]

    # --------------------------------
    # Convert to float
    # --------------------------------

    audio = audio.astype(
        np.float32
    )

    # --------------------------------
    # Resample to 16 kHz
    # --------------------------------

    if original_sample_rate != TARGET_SAMPLE_RATE:

        new_length = int(
            len(audio)
            * TARGET_SAMPLE_RATE
            / original_sample_rate
        )

        audio = resample(
            audio,
            new_length
        )

    # --------------------------------
    # Convert to int16
    # --------------------------------

    audio = np.clip(
        audio,
        -32768,
        32767
    ).astype(
        np.int16
    )

    # --------------------------------
    # Create WAV
    # --------------------------------

    buffer = io.BytesIO()

    with wave.open(
        buffer,
        "wb"
    ) as wav:

        wav.setnchannels(1)

        wav.setsampwidth(2)

        wav.setframerate(
            TARGET_SAMPLE_RATE
        )

        wav.writeframes(
            audio.tobytes()
        )

    buffer.seek(0)

    return buffer.read()