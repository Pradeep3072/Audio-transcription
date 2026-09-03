import sys
import os
import requests

# Get the project root directory
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# Add project root to Python path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


import streamlit as st


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Audio Transcription",
    page_icon="🎙️",
    layout="wide"
)


# ==========================================
# TITLE & SIDEBAR
# ==========================================

st.title("🎙️ AI Audio Transcription")

st.write(
    "Upload an audio file to have it transcribed and corrected by AI."
)

LANGUAGES = {
    "Auto-detect": None,
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Hindi": "hi",
    "Tamil": "ta",
    "Tanglish": "tanglish",
    "Telugu": "te",
    "Malayalam": "ml"
}

st.sidebar.header("Settings")
selected_lang_name = st.sidebar.selectbox("Transcription Language", list(LANGUAGES.keys()))
selected_lang_code = LANGUAGES[selected_lang_name]

st.sidebar.divider()
use_cloud = st.sidebar.toggle("☁️ Use Cloud Whisper (Fast)", value=False)
st.sidebar.caption("When enabled, audio is sent to Groq's cloud for instant transcription instead of running slowly on your local PC.")


# ==========================================
# FILE UPLOAD
# ==========================================

st.subheader("Upload Audio File")

uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a", "ogg"])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("Transcribe File"):
        with st.spinner("Transcribing..."):
            try:
                data = {}
                if selected_lang_code:
                    data["language"] = selected_lang_code
                if use_cloud:
                    data["use_cloud"] = "true"
                    
                response = requests.post(
                    "http://127.0.0.1:8000/transcribe",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Transcription and correction complete!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### 🗣️ Original Transcript:")
                        st.info(result.get("raw_text", ""))
                    with col2:
                        st.write("### ✨ AI Corrected:")
                        st.success(result.get("corrected_text", ""))
                        
                    if result.get("summary"):
                        st.write("### 📝 Summary")
                        st.info(result.get("summary", ""))
                        
                    eval_data = result.get("evaluation")
                    if eval_data:
                        st.write("### 📊 Agent Evaluation")
                        st.write(f"**Grammar & Clarity Score:** {eval_data.get('grammar_score')}/10")
                        st.write(f"**Improvement Summary:** {eval_data.get('readability_improvement')}")
                        st.write("**Specific Changes:**")
                        for change in eval_data.get('changes_made', []):
                            st.write(f"- {change}")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")