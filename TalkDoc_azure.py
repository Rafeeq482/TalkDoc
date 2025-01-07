import openai
import pyaudio
import wave
import streamlit as st
import azure.cognitiveservices.speech as speechsdk

# Azure AI Speech API credentials
azure_api_key = "A7HoBvgDewKVKE4AxOTECa3AZW7UvT9Mv9YZw9uRwti53GqtylxlJQQJ99ALACYeBjFXJ3w3AAAEACOGYICe"
azure_region = "eastus"
openai_api_key = "B08k2G441vX09NJoA6ZHZQ11ztcIL0K88mJi7Wnr5xmA52TJWjGXJQQJ99ALACYeBjFXJ3w3AAABACOGgRro"  # Replace with your Azure OpenAI API key
openai_endpoint = "https://opanai777777777.openai.azure.com/"  # Replace with your Azure OpenAI endpoint
deployment_id = "gpt-35-turbo-16k"  # Replace with your Azure OpenAI deployment ID

# Set up the OpenAI API key and endpoint for Azure OpenAI
openai.api_key = openai_api_key
openai.api_base = openai_endpoint
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"  # Specify the API version if required

# Set up Azure Speech API credentials
speech_config = speechsdk.SpeechConfig(subscription=azure_api_key, region=azure_region)
speech_config.speech_recognition_language = "en-US"

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

def transcribe_audio(file_path):
    """Transcribe audio using Azure Speech-to-Text."""
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    st.text("Transcribing audio...")
    result = speech_recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        raise Exception("No speech could be recognized.")
    else:
        raise Exception(f"Speech recognition failed: {result.error_details}")

def get_azure_openai_response(user_prompt):
    """Get a response from Azure OpenAI based on the user prompt."""
    completion = openai.ChatCompletion.create(
        deployment_id=deployment_id,  # Use the correct deployment ID for Azure OpenAI
        messages=[{"role": "system", "content": "You are a helpful AI doctor."},
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

        # Step 2: Transcribe audio using Azure AI
        transcription = transcribe_audio(audio_file)
        
        # Step 3: Get response from Azure OpenAI
        st.text("Transcription:")
        st.write(transcription)
        
        response = get_azure_openai_response(transcription)
        st.text("Doctor's Response:")
        st.write(response)
        
    except Exception as e:
        st.error(f"Error: {e}")
