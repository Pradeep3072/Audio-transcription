# System Redesign: Integrating Celery & Redis for Background Processing

The goal of this architectural update is to decouple heavy machine learning tasks (Whisper transcription and LLM correction) from the main FastAPI server. By utilizing **Celery** as an asynchronous task queue and **Redis** as the message broker, we can achieve better scalability, non-blocking requests, and higher efficiency.

## User Review Required

> [!IMPORTANT]
> **Redis Requirement:** This architecture requires a Redis server to be running locally or remotely. Since you are on Windows, you will need to run Redis either via Docker, WSL (Windows Subsystem for Linux), or Memurai (a Redis port for Windows). Do you already have Redis installed, or do you have a preference for how to run it?

> [!IMPORTANT]
> **Running Workers:** After this change, running the app will require opening an additional terminal window to run the Celery worker process (e.g., `celery -A Backend.celery_app worker --loglevel=info -P gevent`). 

## Open Questions

1. Do you have a Redis instance running already? If so, what is the connection URL (default is usually `redis://localhost:6379/0`)?
2. For the file uploads, we need to save the uploaded audio files to a disk directory (e.g., `uploads/`) so the Celery worker can pick them up. Is this acceptable?

## Proposed Changes

---

### Dependencies

We need to add the required libraries for Celery and Redis to the environment.

#### [MODIFY] requirements.txt
- Add `celery`
- Add `redis`
- Add `gevent` (Recommended for running Celery on Windows)

---

### Backend Components

We will introduce a new Celery application and task definitions, and remove the heavy model loading from the main API.

#### [NEW] Backend/celery_app.py
- Configure the Celery instance, pointing the broker and backend to Redis.

#### [NEW] Backend/tasks.py
- Globally initialize the `WhisperService` and `TranscriptionCorrectionAgent` inside this file so they only load in the worker processes, not the FastAPI web server.
- Define a Celery task `process_audio_task(filepath, language)` that handles the transcription and LLM correction, and cleans up the temporary file after it is done.

#### [MODIFY] Backend/main.py
- Remove direct imports and initializations of `WhisperService` and `TranscriptionCorrectionAgent`.
- **POST `/transcribe`**: Refactor to save the uploaded file to disk and call `process_audio_task.delay(filepath, language)`. It will now immediately return a `task_id` instead of blocking.
- **GET `/transcribe/status/{task_id}`**: Add this new endpoint for the frontend to poll the status of the background task and retrieve results when ready.
- **WebSocket `/ws/transcribe`**: Update to save the incoming audio bytes to a temp file, trigger the Celery task, and asynchronously poll for its completion before sending the result back to the frontend.

---

### Frontend Components

The Streamlit app needs to be updated to handle the new asynchronous flow for file uploads.

#### [MODIFY] Frontend/app.py
- Update the "File Upload" section to first POST the file, retrieve the `task_id`, and then show a spinner while polling the new `GET /transcribe/status/{task_id}` endpoint until it receives a success or failure status.
- Live microphone WebSocket implementation will remain largely unchanged on the frontend, as the backend will handle the asynchronous waiting internally.

## Verification Plan

### Automated/Local Tests
- Install Redis (if not already running) and start the server.
- Install new requirements (`pip install -r requirements.txt`).
- Start the FastAPI backend: `uvicorn Backend.main:app --reload`.
- Start the Celery worker: `celery -A Backend.celery_app worker -P gevent --loglevel=info`.
- Start Streamlit: `streamlit run Frontend/app.py`.

### Manual Verification
- Test file upload: Verify that uploading a file returns immediately with a spinner in the UI while polling, and eventually displays the results.
- Test live transcription: Speak into the microphone and verify that transcripts are still correctly generated and returned.
