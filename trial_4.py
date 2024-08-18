import streamlit as st
from pydub import AudioSegment
from pydub.playback import play
import tempfile
import os
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import speech_recognition as sr

# Function to record audio using ffmpeg
def record_audio(duration):
    st.write("Recording for {} seconds...".format(duration))
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    os.system(f"ffmpeg -y -f alsa -t {duration} -i default {temp_audio_file.name}")
    st.write("Recording complete.")
    return temp_audio_file.name

# The rest of your code remains mostly the same

# Initialize the recognizer 
r = sr.Recognizer()

# Your Streamlit app layout and logic remains the same
