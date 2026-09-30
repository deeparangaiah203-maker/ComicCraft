import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY not found")
        return None
    try:
        
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Gemini client error: {e}")
        return None