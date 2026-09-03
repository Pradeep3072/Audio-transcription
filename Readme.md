# 🎙️ AI Audio Transcription Pipeline

A full-stack application that provides file-upload transcription capabilities using state-of-the-art AI models.

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **AI Models:** 
  - [OpenAI Whisper](https://github.com/openai/whisper) (Speech-to-Text, Multi-language Support)
  - [Groq LLM API](https://groq.com/) (Fast AI Proofreading & Summarization via Langchain)

## 📦 Key Libraries & Packages Used

### Core Frameworks
- `streamlit`: Builds the interactive web user interface.
- `fastapi`: High-performance backend API framework.
- `uvicorn`: ASGI web server to run the FastAPI application.

### Audio Processing & AI
- `openai-whisper`: The core Automatic Speech Recognition (ASR) model used to convert speech to text.
- `langchain` & `langchain-groq`: Frameworks used to orchestrate the AI Agent workflow for transcript proofreading, summarization, and generating evaluation metrics via the Groq API.
- `requests`: Used by the frontend to send HTTP POST requests (file uploads) to the backend.

---

## 🔄 Workflow & Architecture

The application is split into a **Frontend (Streamlit)** and a **Backend (FastAPI)**. It supports the following workflow:

### 1. Audio File Upload
This method allows users to upload pre-recorded audio files for bulk transcription.

**How it works:**
1. **Upload Interface:** The user navigates to the Streamlit app and uploads an audio file (e.g., `.wav`, `.mp3`).
2. **HTTP Request:** The frontend sends the file as form-data via a standard HTTP POST request.
   - **Endpoint:** `POST http://127.0.0.1:8000/transcribe`
3. **Transcription:** The FastAPI backend receives the `UploadFile` (and the `language` selection), reads the raw bytes, and passes them directly to the **Whisper** model.
4. **Response:** The backend returns a JSON payload containing the original filename and the complete transcript, which Streamlit immediately displays to the user.

### 2. AI Proofreading & Summarization Agent
To enhance the raw Whisper transcription, the backend employs a **Langchain Agent** powered by a Groq LLM (`openai/gpt-oss-20b`).
- **Correction:** The agent proofreads the raw transcript, fixing grammar, punctuation, and contextual errors.
- **Summarization:** The agent provides a concise summary of the transcribed text.
- **Evaluation Matrix:** The agent self-evaluates its corrections, providing a grammar score (1-10), a readability improvement summary, and a list of specific changes made.
- **Asynchronous Execution:** Heavy CPU-bound models (Whisper) and synchronous API calls (Groq) are wrapped in `asyncio.to_thread()` in the FastAPI routes to prevent event loop deadlocks, ensuring the server remains highly responsive.

### 3. Multi-Language Support
The application fully supports Whisper's native 99-language capabilities.
- By default, the app uses an **Auto-detect** feature where Whisper analyzes the first few seconds of audio to guess the language.
- Users can manually select their spoken language (e.g., Spanish, French, Japanese, Tamil) from the **Settings Sidebar**.
- Explicitly selecting the language improves transcription speed and prevents Whisper from guessing incorrectly on very short audio segments.
- The language choice is passed to the backend via HTTP Form Data.

---

## 🚀 How to Run

You need to start both the backend server and the frontend application simultaneously.

**1. Start the Backend (FastAPI)**
```bash
uvicorn Backend.main:app --reload
```
*(The backend runs on http://127.0.0.1:8000)*

**2. Start the Frontend (Streamlit)**
```bash
streamlit run Frontend/app.py
```
*(The frontend runs on http://localhost:8501)*
