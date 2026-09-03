import whisper
import tempfile
import os
from dotenv import load_dotenv

class WhisperService:

    def __init__(self):
        
        # Load environment variables from .env file
        load_dotenv()

        model_size = os.getenv("WHISPER_MODEL", "small")
        print(f"[Whisper] Loading Whisper {model_size} model...")

        self.model = whisper.load_model(model_size)

        print("[Whisper] Whisper model loaded!")


    def transcribe(self, audio_bytes: bytes, language: str = None):

        temp_file = None

        try:

            # =====================================
            # Create temporary WAV file
            # =====================================

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as f:

                f.write(audio_bytes)

                temp_file = f.name


            print(
                f"[Whisper] Received audio: "
                f"{len(audio_bytes)} bytes. Language: {language}"
            )


            # =====================================
            # Transcribe
            # =====================================

            if language:
                result = self.model.transcribe(
                    temp_file,
                    fp16=False,
                    language=language
                )
            else:
                result = self.model.transcribe(
                    temp_file,
                    fp16=False
                )


            text = result["text"].strip()


            print(
                f"[Whisper] Transcript: {text}"
            )


            return text


        except Exception as e:

            print(
                f"[Whisper error]: {e}"
            )

            return ""


        finally:

            # =====================================
            # Delete temporary file
            # =====================================

            if temp_file and os.path.exists(temp_file):

                os.remove(temp_file)