# 🎙️ AI Audio Transcription Pipeline

A full-stack application that provides real-time live audio transcription and file-upload transcription capabilities using state-of-the-art AI models.

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Real-Time Communication:** WebRTC & WebSockets
- **AI Models:** 
  - [OpenAI Whisper](https://github.com/openai/whisper) (Speech-to-Text, Multi-language Support)
  - [Silero VAD](https://github.com/snakers4/silero-vad) (Voice Activity Detection)
  - [Groq LLM API](https://groq.com/) (Fast AI Proofreading & Summarization via Langchain)

## 📦 Key Libraries & Packages Used

### Core Frameworks
- `streamlit`: Builds the interactive web user interface.
- `fastapi`: High-performance backend API framework.
- `uvicorn`: ASGI web server to run the FastAPI application.

### Audio Capture & Networking
- `streamlit-webrtc`: Enables real-time audio streaming from the user's browser microphone using WebRTC.
- `websocket-client`: Facilitates real-time, bidirectional communication between the frontend audio processor and the backend.
- `requests`: Used by the frontend to send HTTP POST requests (file uploads) to the backend.

### Audio Processing & AI
- `openai-whisper`: The core Automatic Speech Recognition (ASR) model used to convert speech to text.
- `torch` & `silero-vad`: Used locally on the frontend to process incoming audio streams and detect human speech vs. silence.
- `langchain` & `langchain-groq`: Frameworks used to orchestrate the AI Agent workflow for transcript proofreading, summarization, and generating evaluation metrics via the Groq API.
- `av`, `numpy`, `scipy`, `wave`: Various utilities for manipulating audio frames, converting stereo to mono, and structuring raw audio data into WAV format.

---

## 🔄 Workflow & Architecture

The application is split into a **Frontend (Streamlit)** and a **Backend (FastAPI)**. It supports two main workflows:

### 1. Live Microphone Transcription
This method captures your voice in real-time and transcribes it segment by segment.

**How it works:**
1. **Audio Capture:** The user starts the microphone in the Streamlit UI. `streamlit-webrtc` captures the audio stream via the browser.
2. **Voice Activity Detection (VAD):** As audio frames stream in, the `AudioProcessor` evaluates them using the **Silero VAD** model. It determines the probability of human speech.
3. **Buffering:** When speech is detected (probability > 60%), the frames are buffered. When continuous silence is detected (speech ends), the buffered frames are compiled into a temporary in-memory WAV file.
4. **WebSocket Transmission:** The frontend opens a WebSocket connection to the backend endpoint:
   - **Endpoint:** `ws://127.0.0.1:8000/ws/transcribe?language={selected_language}`
   - It sends the binary WAV data to the backend.
5. **Transcription:** The backend receives the bytes, saves them to a temporary file, and runs the **Whisper** model to generate the transcript.
6. **Displaying Results:** The backend sends the text back through the WebSocket as JSON. The frontend `AudioProcessor` places this text into a thread-safe Queue. The Streamlit UI continuously polls this queue (using `st.rerun()`) and updates the display in near real-time.

### 2. Audio File Upload
This method allows users to upload pre-recorded audio files for bulk transcription.

**How it works:**
1. **Upload Interface:** The user navigates to the "File Upload" tab in Streamlit and uploads an audio file (e.g., `.wav`, `.mp3`).
2. **HTTP Request:** The frontend sends the file as form-data via a standard HTTP POST request.
   - **Endpoint:** `POST http://127.0.0.1:8000/transcribe`
3. **Transcription:** The FastAPI backend receives the `UploadFile` (and the `language` selection), reads the raw bytes, and passes them directly to the **Whisper** model.
4. **Response:** The backend returns a JSON payload containing the original filename and the complete transcript, which Streamlit immediately displays to the user.

### 3. AI Proofreading & Summarization Agent
To enhance the raw Whisper transcription, the backend employs a **Langchain Agent** powered by a Groq LLM (`openai/gpt-oss-20b`).
- **Correction:** The agent proofreads the raw transcript, fixing grammar, punctuation, and contextual errors.
- **Summarization:** The agent provides a concise summary of the transcribed text.
- **Evaluation Matrix:** The agent self-evaluates its corrections, providing a grammar score (1-10), a readability improvement summary, and a list of specific changes made.
- **Asynchronous Execution:** Heavy CPU-bound models (Whisper) and synchronous API calls (Groq) are wrapped in `asyncio.to_thread()` in the FastAPI routes to prevent event loop deadlocks, ensuring the server remains highly responsive to WebSockets and other HTTP requests.

### 4. Multi-Language Support
The application fully supports Whisper's native 99-language capabilities.
- By default, the app uses an **Auto-detect** feature where Whisper analyzes the first few seconds of audio to guess the language.
- Users can manually select their spoken language (e.g., Spanish, French, Japanese, Tamil) from the **Settings Sidebar**.
- Explicitly selecting the language improves transcription speed and prevents Whisper from guessing incorrectly on very short audio segments.
- The language choice is passed to the backend via HTTP Form Data (for file uploads) or WebSocket Query Parameters (for live transcription).

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
