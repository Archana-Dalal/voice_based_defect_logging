This project is an AI-powered voice-based defect logging system for steel sheets, leveraging Streamlit, SpeechRecognition, and Groq's LLM. It enables simultaneous multi-defect registration from voice input, 
ensuring real-time, high-accuracy tracking and seamless integration with Google Sheets as database.

Features:
Voice Input: Records and transcribes defect details.
AI Extraction: Uses Groq's LLM to extract key details.
Google Sheets Integration: Automatically logs data.
Streamlit UI: Interactive form for data validation.

Tech Stack:
Frontend: Streamlit
Speech Processing: SpeechRecognition, Pyttsx3
AI/LLM: Groq
Database: Google Sheets via gspread
Authentication: OAuth2 (Google API)
Backend: Python

Impact & Uniqueness:
Time Efficiency: Manual defect logging takes 1-2 minutes per entry, while this system completes it in under 15 seconds, boosting productivity by over 150% and more, depending on the operator's expertise.
Enhanced Accuracy: AI-driven extraction minimizes human error, ensuring precise defect tracking.
Real-Time Analysis: Enables instant defect detection and storage, improving manufacturing workflows.
Scalability: Can be integrated with larger quality control systems for enhanced monitoring.
User-Centric Design: Combines voice recognition and AI for effortless defect reporting.
