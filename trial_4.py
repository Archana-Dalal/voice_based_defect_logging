import streamlit as st
import sounddevice as sd
import numpy as np
import io
import re
import tempfile
import os
import gspread
from scipy.io.wavfile import write
from oauth2client.service_account import ServiceAccountCredentials
import speech_recognition as sr

# Initialize the recognizer 
r = sr.Recognizer()

# Function to record audio using sounddevice
def record_audio(duration, fs=44100):
    st.write("Recording for {} seconds...".format(duration))
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    st.write("Recording complete.")
    return recording, fs

# Function to save the recorded audio as a WAV file
def save_audio_to_wav(audio_data, fs):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        write(temp_audio_file.name, fs, audio_data)
        return temp_audio_file.name

# Function to parse the recognized text
def parse_text(text):
    coil_id = re.search(r'coil id (\w+)', text)
    start_length = re.search(r'start length (\w+)', text)
    stop_length = re.search(r'stop length (\w+)', text)
    defect = re.search(r'defect (.+?) severity', text)
    severity = re.search(r'severity (\w+)', text)
    position = re.search(r'position (\w+)', text)
    
    return (
        coil_id.group(1) if coil_id else None,
        start_length.group(1) if start_length else None,
        stop_length.group(1) if stop_length else None,
        defect.group(1) if defect else None,
        severity.group(1) if severity else None,
        position.group(1) if position else None
    )

# Authenticate and access Google Sheets
def access_google_sheet(sheet_name="SteelSheetDefects"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"C:\Users\archa\Downloads\voice-based-defect-logging-6b6a427015be.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("defects").sheet1
    return sheet

# Function to append defect info to Google Sheets
def append_to_google_sheet(coil_id, start_length, stop_length, defect, severity, position):
    sheet = access_google_sheet()
    sheet.append_row([coil_id, start_length, stop_length, defect, severity, position])

# Initialize Streamlit session state to store transcribed data
if 'coil_id' not in st.session_state:
    st.session_state['coil_id'] = ""
if 'start_length' not in st.session_state:
    st.session_state['start_length'] = ""
if 'stop_length' not in st.session_state:
    st.session_state['stop_length'] = ""
if 'defect' not in st.session_state:
    st.session_state['defect'] = ""
if 'severity' not in st.session_state:
    st.session_state['severity'] = ""
if 'position' not in st.session_state:
    st.session_state['position'] = ""

# Streamlit app layout
st.title("Steel Sheet Defect Registration")

# Two columns for layout
col1, col2 = st.columns(2)

with col1:
    st.write("Click the button below to record your voice for defect registration. Please include details like Coil ID, start length, stop length, defect, severity, and position in your speech.")

    if st.button("Record for 20 seconds"):
        duration = 20  # seconds
        audio_data, fs = record_audio(duration)
        
        # Save the recorded audio to a WAV file
        temp_audio_path = save_audio_to_wav(audio_data, fs)
        
        try:
            # Use the saved audio file for speech recognition
            with sr.AudioFile(temp_audio_path) as source:
                audio = r.record(source)
                MyText = r.recognize_google(audio).lower()
                st.write("You said:", MyText)

                coil_id, start_length, stop_length, defect, severity, position = parse_text(MyText)

                # Store the extracted values in session state
                st.session_state['coil_id'] = coil_id if coil_id else ""
                st.session_state['start_length'] = start_length if start_length else ""
                st.session_state['stop_length'] = stop_length if stop_length else ""
                st.session_state['defect'] = defect if defect else ""
                st.session_state['severity'] = severity if severity else ""
                st.session_state['position'] = position if position else ""

        except sr.RequestError as e:
            st.write(f"Could not request results; {e}")
        except sr.UnknownValueError:
            st.write("Could not understand audio")

        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

with col2:
    coil_id = st.text_input("Coil ID", value=st.session_state['coil_id'])
    start_length = st.text_input("Start Length", value=st.session_state['start_length'])
    stop_length = st.text_input("Stop Length", value=st.session_state['stop_length'])
    defect = st.text_input("Defect", value=st.session_state['defect'])
    severity = st.text_input("Severity", value=st.session_state['severity'])
    position = st.text_input("Position", value=st.session_state['position'])

    if st.button("Save to Google Sheets"):
        if coil_id and start_length and stop_length and defect and severity and position:
            st.write("Status: Successful")
            append_to_google_sheet(coil_id, start_length, stop_length, defect, severity, position)
        else:
            st.write("Status: Unsuccessful. Please ensure all fields are filled.")
st.write("Streamlit script ended")
