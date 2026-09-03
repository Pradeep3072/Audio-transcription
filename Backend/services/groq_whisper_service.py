import os
import tempfile
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqWhisperService:
    def __init__(self):
        print("Initializing Groq Whisper Service...")
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("[WARNING] GROQ_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)
        print("Groq Whisper Service ready.")

    def transcribe(self, audio_bytes: bytes, language: str = None) -> str:
        """
        Transcribes audio using Groq's whisper-large-v3 model.
        """
        if not self.client:
            print("[Groq Whisper Error]: API key missing.")
            return ""

        temp_file = None
        try:
            # Write bytes to temp file so Groq SDK can read it
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_bytes)
                temp_file = f.name

            # Open the file for the API call
            with open(temp_file, "rb") as audio_file:
                # Groq API doesn't support 'None' for language, it requires the actual code or omitting it.
                kwargs = {
                    "file": (os.path.basename(temp_file), audio_file),
                    "model": "whisper-large-v3",
                }
                
                if language:
                    kwargs["language"] = language

                # Make the API call
                transcription = self.client.audio.transcriptions.create(**kwargs)
                return transcription.text

        except Exception as e:
            print(f"[Groq Whisper error]: {e}")
            return ""
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
