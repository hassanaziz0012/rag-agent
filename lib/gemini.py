from dotenv import load_dotenv
from google import genai
import os

def load_api_key():
    """Load the Gemini API key from environment variables or Colab."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        from google.colab import userdata
        api_key = userdata.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
    return api_key

def build_prompt(query, results):
    """Build the prompt for the LLM."""
    return f"""
You are an LLM tasked with answering questions on the book "Purpose and Profit" by Dan Koe.

This is how the author described the book:
```
Transform Your Relationship With Money & Discover Your Life's Work
Money controls most people's lives, but it doesn't have to. Money is only superficial to the superficial. There is, in fact, a way to merge purpose and profit to create a life filled with work you don't want to escape from.
```

I'll give you the search query and the top 5 paragraphs from the book that are most relevant to the user's search query. Your job is to use those 5 paragraphs to answer the user's question as best as you can.

- Do not deviate from the given paragraphs.
- If you don't have an answer, say "I don't know".
- Keep your answer concise and information-dense.

Here is the user's search query:
{query}

Here are the top 5 paragraphs from the book that are most relevant to the user's search query:
{results}
"""

def generate_response(api_key, prompt):
    """Generate a response from the LLM."""
    llm = genai.Client(api_key=api_key)
    resp = llm.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
    return resp.text
