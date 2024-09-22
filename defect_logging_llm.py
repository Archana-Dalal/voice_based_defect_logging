import streamlit as st
import speech_recognition as sr
import pyttsx3
import re
import tempfile
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from groq import Groq

# Initialize the recognizer 
r = sr.Recognizer()

# Function to convert text to speech
def SpeakText(command):
    engine = pyttsx3.init()
    engine.say(command)
    engine.runAndWait()


#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
# Function to extract data using the LLM
def extract_data_with_llm(transcribed_text):
    client = Groq(api_key='your api')  # Replace 'api_key' with your actual API key

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Obtain the following details from the text: coil ID, start length, stop length, defect, severity, and position and then give the response similar to example: coil id 1 start length 1 stop length 1 defect x severity medium position left. Do not assume any default values. In case a value is not mentioned or available in the text, skip the value and keep the format of the sentence same. For example if the text is: starting from length 3 to 19, then output: coil id start length 3 stop length 19 defect severity position. Here is the text: {transcribed_text}",
            }
        ],
        model="llama3-70b-8192",
    )

    # Access the content directly from the ChatCompletionMessage object
    response = chat_completion.choices[0].message.content
    return response

def access_google_sheet(sheet_name="SteelSheetDefects"):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(r"json file", scope)
    client = gspread.authorize(creds)
    sheet = client.open("defects").sheet1
    return sheet

# Function to append defect info to Google Sheets
def append_to_google_sheet(coil_id, start_length, stop_length, defect, severity, position):
    sheet = access_google_sheet()
    sheet.append_row([coil_id, start_length, stop_length, defect, severity, position])

# Function to parse LLM response
def parse_llm_response(response):
    coil_id = re.search(r'coil id (.+?) start length', response, re.IGNORECASE)
    start_length = re.search(r'start length (.+?) stop length', response, re.IGNORECASE)
    stop_length = re.search(r'stop length (.+?) defect', response, re.IGNORECASE)
    defect = re.search(r'defect (.+?) severity', response, re.IGNORECASE)
    severity = re.search(r'severity (.+?) position', response, re.IGNORECASE)
    position = re.search(r'position (\w+)', response, re.IGNORECASE)
    
    # Append new values to the existing session state values
    new_coil_id = coil_id.group(1) if coil_id else None
    new_start_length = start_length.group(1) if start_length else None
    new_stop_length = stop_length.group(1) if stop_length else None
    new_defect = defect.group(1) if defect else None
    new_severity = severity.group(1) if severity else None
    new_position = position.group(1) if position else None

    return (
        new_coil_id,
        new_start_length,
        new_stop_length,
        new_defect,
        new_severity,
        new_position
    )

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

st.markdown("""
    <style>
    .stApp {
        background-color: #008080;  /* Change this color to your desired background color */
        padding: 20px;  /* Optional: Add padding if needed */
    }
    .stButton>button {
        background-color: #262730;
        color: #F6EDE3;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 20px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .stTextInput>div>input {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
    }
    .stTitle {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


st.markdown('<div style="background-color: #008080; min-height: 1vh; padding: 20px;">', unsafe_allow_html=True)


st.title("Steel Sheet Defect Registration")

# Two columns for layout
col1, col2 = st.columns(2)

with col1:
    st.write("Click the button below to record your voice for defect registration.")

    if st.button("Record for 20 seconds"):
        with sr.Microphone() as source:
            st.write("Adjusting for ambient noise, please wait...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            
            st.write("Recording...")
            audio = r.listen(source, timeout=20, phrase_time_limit=20)
            st.write("Recording complete. Recognizing...")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio.get_wav_data())
                temp_audio_path = temp_audio_file.name
            
            try:
                MyText = r.recognize_google(audio).lower()
                st.markdown("**You said:**")
                st.write(MyText)

                # Extract data using LLM
                llm_response = extract_data_with_llm(MyText)
                #st.markdown("**LLM Response:**")
                #st.write(llm_response)
                
                # Parse the LLM response
                coil_id, start_length, stop_length, defect, severity, position = parse_llm_response(llm_response)

                # Update session state with the parsed values
                st.session_state['coil_id'] = coil_id if coil_id else st.session_state['coil_id']
                st.session_state['start_length'] = start_length if start_length else st.session_state['start_length']
                st.session_state['stop_length'] = stop_length if stop_length else st.session_state['stop_length']

                # Append defect and severity to existing values
                if defect:
                    st.session_state['defect'] += f", {defect}" if st.session_state['defect'] else defect
                if severity:
                    st.session_state['severity'] += f", {severity}" if st.session_state['severity'] else severity

                st.session_state['position'] = position if position else st.session_state['position']

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
            
            # Clear the session state fields
            st.session_state['coil_id'] = ""
            st.session_state['start_length'] = ""
            st.session_state['stop_length'] = ""
            st.session_state['defect'] = ""
            st.session_state['severity'] = ""
            st.session_state['position'] = ""
            
        else:
            st.write("Status: Unsuccessful. Please ensure all fields are filled.")
