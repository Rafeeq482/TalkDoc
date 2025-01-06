import openai
import pyaudio
import wave
import requests
import time
import streamlit as st

# AssemblyAI API Key
assembly_api_key = "faa6fbaaf05d4b09930abfa163b8c42b"
openai_api_key = "be2df831fcb1442aa5843b9e060dbf56"
openai_base_url = "https://api.aimlapi.com/v1"

# Headers for AssemblyAI authentication
headers = {
    "authorization": assembly_api_key,
    "content-type": "application/json"
}

# OpenAI system prompt
system_prompt = "You are Doctor give prescription according to user prompt. Be descriptive and helpful."

# Set up the OpenAI API key and base URL
openai.api_key = openai_api_key
openai.api_base = openai_base_url

def record_audio(output_file, duration=10, rate=16000, chunk=1024):
    """Record audio from the microphone."""
    p = pyaudio.PyAudio()
    
    stream = p.open(format=pyaudio.paInt16,  # 16-bit audio format
                    channels=1,             # Mono audio
                    rate=rate,              # Sampling rate
                    input=True,
                    frames_per_buffer=chunk)
    
    st.text("Recording... Please speak into the microphone.")
    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    st.text("Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a file
    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

def upload_audio(file_path):
    """Upload the recorded audio to AssemblyAI."""
    upload_endpoint = "https://api.assemblyai.com/v2/upload"
    with open(file_path, "rb") as f:
        response = requests.post(upload_endpoint, headers=headers, data=f)
    return response.json()["upload_url"]

def transcribe_audio(audio_url):
    """Submit the transcription request."""
    transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
    transcript_request = {"audio_url": audio_url}
    response = requests.post(transcript_endpoint, headers=headers, json=transcript_request)
    return response.json()["id"]

def get_transcription_result(transcript_id):
    """Retrieve the transcription result."""
    transcript_result_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    while True:
        response = requests.get(transcript_result_endpoint, headers=headers)
        status = response.json()["status"]
        if status == "completed":
            return response.json()["text"]
        elif status == "failed":
            raise Exception("Transcription failed.")
        # Wait before checking again
        time.sleep(5)

def get_openai_response(user_prompt):
    """Get a response from OpenAI based on the user prompt."""
    completion = openai.ChatCompletion.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": user_prompt}],
        temperature=0.7,
        max_tokens=256,
    )
    return completion.choices[0].message['content']

# Streamlit UI setup
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8ff;
        color: #333333;
    }
    .sidebar .sidebar-content {
        background-color: #f9f9f9;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        font-size: 16px;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Welcome to the Medical Assistant Chatbot!")
st.code('''
▀▀█▀▀ ─█▀▀█ ░█─── ░█─▄▀ ░█▀▀▄ ░█▀▀▀█ ░█▀▀█ 
─░█── ░█▄▄█ ░█─── ░█▀▄─ ░█─░█ ░█──░█ ░█─── 
─░█── ░█─░█ ░█▄▄█ ░█─░█ ░█▄▄▀ ░█▄▄▄█ ░█▄▄█''')
st.write("I am TalkDoc, an artificial intelligence powered assistant that helps you find the right medicines for your symptoms.")
st.write("I can provide you with information on the best medicines to take for a variety of ailments.")
st.write("Go on!")

st.sidebar.subheader("Instructions")
st.sidebar.text("""
1. Press the button below to record your voice.
2. Wait for the transcription to complete.
3. The AI Doctor will generate a response based on your input.
""")

if st.button("Say symptoms"):
    audio_file = "mic_recording.wav"
    record_duration = 6  # Record for 6 seconds
    
    try:
        # Step 1: Record audio
        record_audio(audio_file, duration=record_duration)

        # Step 2: Upload audio and transcribe
        st.text("Uploading and transcribing audio...")
        audio_url = upload_audio(audio_file)
        transcript_id = transcribe_audio(audio_url)
        transcription = get_transcription_result(transcript_id)
        
        # Step 3: Get response from OpenAI
        st.text("Transcription:")
        st.write(transcription)
        
        response = get_openai_response(transcription)
        st.text("Doctor's Response:")
        st.write(response)
        
    except Exception as e:
        st.error(f"Error: {e}")
