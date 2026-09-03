import asyncio
from fastapi import FastAPI, WebSocket, UploadFile, File, Form, Query
import os
from Backend.services.whisper_service import WhisperService
from Backend.services.groq_whisper_service import GroqWhisperService
from Backend.agents.transcription_agent import TranscriptionCorrectionAgent


app = FastAPI()


# ==========================================
# LOAD WHISPER & AGENT
# ==========================================

whisper_service = WhisperService()
groq_whisper_service = GroqWhisperService()
correction_agent = TranscriptionCorrectionAgent()


# ==========================================
# WEBSOCKET
# ==========================================

@app.websocket("/ws/transcribe")
async def websocket_transcribe(
    websocket: WebSocket,
    language: str = Query(None),
    use_cloud: str = Query("false")
):

    await websocket.accept()

    print("[WebSocket] Whisper WebSocket connected")


    try:

        while True:

            # Receive complete WAV audio
            audio_bytes = await websocket.receive_bytes()


            print(
                f"[WebSocket] Received audio: "
                f"{len(audio_bytes)} bytes"
            )


            # Filter language for Whisper (it doesn't support 'tanglish')
            whisper_lang = None if language == "tanglish" else language

            # Select the appropriate whisper service
            active_whisper_service = groq_whisper_service if use_cloud.lower() == "true" else whisper_service

            # Send to Whisper without blocking the event loop
            raw_text = await asyncio.to_thread(
                active_whisper_service.transcribe,
                audio_bytes,
                whisper_lang
            )

            # Return raw transcript (no agent correction for live transcription)
            await websocket.send_json({
                "type": "transcript",
                "raw_text": raw_text,
                "corrected_text": raw_text,
                "summary": "",
                "evaluation": None
            })


    except Exception as e:

        print(
            f"[WebSocket] error: {e}"
        )


    finally:

        print(
            "[WebSocket] Whisper WebSocket disconnected"
        )


# ==========================================
# FILE UPLOAD TRANSCRIPTION
# ==========================================

@app.post("/transcribe")
async def transcribe_file(
    file: UploadFile = File(...),
    language: str = Form(None),
    use_cloud: str = Form("false")
):
    print(f"[Upload] Received file: {file.filename}. Language: {language}. Cloud: {use_cloud}")
    
    # Read the file bytes
    audio_bytes = await file.read()
    
    # Filter language for Whisper
    whisper_lang = None if language == "tanglish" else language

    # Select the appropriate whisper service
    active_whisper_service = groq_whisper_service if use_cloud.lower() == "true" else whisper_service

    # Send to Whisper without blocking event loop
    raw_text = await asyncio.to_thread(
        active_whisper_service.transcribe,
        audio_bytes,
        whisper_lang,
        file.filename
    )
    
    # Correct with Agent without blocking event loop
    agent_result = await asyncio.to_thread(
        correction_agent.correct,
        raw_text,
        language
    )
    
    return {
        "filename": file.filename,
        "raw_text": raw_text,
        "corrected_text": agent_result.get("corrected_text", ""),
        "summary": agent_result.get("summary", ""),
        "evaluation": agent_result.get("evaluation")
    }
# Trigger reload
