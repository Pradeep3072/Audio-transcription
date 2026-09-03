import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from Backend.models.schemas import CorrectedTranscript

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
load_dotenv(dotenv_path)

class TranscriptionCorrectionAgent:
    def __init__(self):
        print("[Agent] Initializing Langchain Groq Agent...")
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            print("[WARNING] GROQ_API_KEY is not set or not loaded correctly from .env")
            self.structured_llm = None
        else:
            self.llm = ChatGroq(
                model="openai/gpt-oss-20b", 
                temperature=0.2, 
                api_key=self.api_key
            )
            self.structured_llm = self.llm.with_structured_output(CorrectedTranscript)
        
    def correct(self, raw_text: str, language: str = None) -> dict:
        if not raw_text or not raw_text.strip():
            return {"corrected_text": "", "summary": "", "evaluation": None}
            
        if not self.structured_llm:
            print("[WARNING] Skipping correction because GROQ_API_KEY is missing.")
        lang_hint = f" The expected language is '{language}'." if language else ""
        if language == "tanglish":
            lang_hint += " 'Tanglish' means a mix of Tamil and English. The raw text may contain a messy mix of Tamil script and English script. Read both carefully, and rewrite the entire sentence into clean, natural-sounding phonetic Tanglish using ONLY the English (Latin) alphabet."
            
        prompt = f"""
        You are an expert polyglot audio transcription proofreader.
        Review the following raw transcription.{lang_hint} First, identify the language of the text.
        Then, fix any spelling, grammatical, or punctuation errors in that specific language. 
        Ensure that the corrections follow the grammar rules of the detected language (e.g., Tamil, Hindi, Spanish, English, Tanglish, etc.).
        Keep the corrected text in the ORIGINAL language (or the language specified). Do NOT translate it to English.
        Do NOT add external information or change the original meaning of the speaker.
        Then, provide a concise summary of the transcribed text capturing its main points.
        Finally, evaluate your own corrections.
        
        Raw Transcription:
        {raw_text}
        """
        
        try:
            print("[Agent] Sending transcript to Groq for correction...")
            result = self.structured_llm.invoke(prompt)
            if hasattr(result, "dict"):
                return result.dict()
            elif hasattr(result, "model_dump"):
                return result.model_dump()
            elif isinstance(result, dict):
                return result
            else:
                return {"corrected_text": raw_text, "summary": "", "evaluation": None}
        except Exception as e:
            error_msg = str(e)
            print(f"[Agent Error]: {error_msg}")
            return {"corrected_text": raw_text, "summary": f"⚠️ AI Correction Failed: {error_msg}", "evaluation": None}
