from Backend.services.whisper_service import transcribe_audio

text=transcribe_audio("uploads/tests1.mp3")

print("\n Transcript")
print(text)
