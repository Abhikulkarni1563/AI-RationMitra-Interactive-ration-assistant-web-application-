import os
import time
import nltk
import speech_recognition as sr
from gtts import gTTS
from dotenv import load_dotenv
import google.generativeai as genai
from helpers import parse_ration_request, update_stock

# -------------------- Setup --------------------
nltk.download('punkt')
recognizer = sr.Recognizer()

# Load Gemini API Key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Instruction for Gemini
SYSTEM_INSTRUCTION = (
    "You are 'Ration Mitraa', an AI assistant for an Indian rural-based ration vending machine. "
    "Your job is to guide users with helpful and clear answers about ration stock, distribution, quotas, "
    "eligibility, pricing, and government schemes. Speak in a way that’s simple for rural users."
)

# -------------------- Core Chatbot Logic --------------------
def ration_mitraa_chatbot(user_input):
    """
    Process user query to either update stock or return Gemini response.
    """
    try:
        user_id = "demo_user"  # Replace with actual ID from session if needed
        orders = parse_ration_request(user_input)

        if orders:
            return update_stock(user_id, orders)

        # Fallback to Gemini AI
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content([
            {"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION + "\nUser Query: " + user_input}]}
        ])
        return response.text.strip()
    except Exception as e:
        print("🔴 Gemini error:", e)
        return "⚠️ Unable to generate response at the moment. Please try again later."

# -------------------- Voice Input --------------------
def listen_to_voice():
    """
    Captures and converts speech to text using Google's speech recognition.
    """
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio)
            print(f"✅ You said: {query}")
            return query
        except sr.UnknownValueError:
            print("❌ Could not understand voice.")
            return None
        except sr.RequestError as e:
            print("❌ Speech recognition error:", e)
            return None

# -------------------- Text-to-Speech Output --------------------
def speak_response(text):
    """
    Converts AI text to speech and saves to static/response.mp3.
    """
    try:
        audio_path = "static/response.mp3"
        tts = gTTS(text=text, lang="en")
        tts.save(audio_path)
        time.sleep(1)  # Ensure file is written
        return audio_path
    except Exception as e:
        print("🔴 TTS error:", e)
        return None
