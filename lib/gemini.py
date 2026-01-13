from dotenv import load_dotenv
from google import genai
import time
import os

def load_api_key():
    """Load the Gemini API key from environment variables or Colab."""
    load_dotenv()
    varname = "GEMINI_API_KEY_2"
    api_key = os.getenv(varname)
    if not api_key:
        from google.colab import userdata
        api_key = userdata.get(varname)
    if not api_key:
        raise ValueError(f"{varname} not found in .env file")
    return api_key

def generate_response(api_key, prompt):
    """Generate a response from the LLM."""
    llm = genai.Client(api_key=api_key)
    resp = llm.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return resp.text

def generate_stream_response(api_key, prompt):
    """Generate a streaming response from the LLM."""
    llm = genai.Client(api_key=api_key)
    resp = llm.models.generate_content_stream(model="gemini-3-flash-preview", contents=prompt)
    for chunk in resp:
        yield chunk.text
