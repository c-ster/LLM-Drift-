import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from mistralai.client import MistralClient
import google.generativeai as genai

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROK_API_KEY = os.getenv("GROK_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- API Endpoints ---
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# --- LLM Client Initialization ---
try:
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    else:
        openai_client = None
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    openai_client = None

try:
    if CLAUDE_API_KEY:
        anthropic_client = Anthropic(api_key=CLAUDE_API_KEY)
    else:
        anthropic_client = None
except Exception as e:
    print(f"Error initializing Anthropic client: {e}")
    anthropic_client = None

try:
    if MISTRAL_API_KEY:
        mistral_client = MistralClient(api_key=MISTRAL_API_KEY)
    else:
        mistral_client = None
except Exception as e:
    print(f"Error initializing Mistral client: {e}")
    mistral_client = None

try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        gemini_model = None
except Exception as e:
    print(f"Error initializing Gemini client: {e}")
    gemini_model = None

try:
    if DEEPSEEK_API_KEY:
        deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
    else:
        deepseek_client = None
except Exception as e:
    print(f"Error initializing Deepseek client: {e}")
    deepseek_client = None

# --- LLM Query Functions ---

def get_chatgpt_response(question: str) -> str:
    """Queries the ChatGPT API."""
    if not openai_client:
        return "OpenAI API key not configured or client initialization failed."
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing concise and neutral answers."},
                {"role": "user", "content": question}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error querying ChatGPT: {e}")
        return f"Error: Could not get response from ChatGPT."

def get_claude_response(question: str) -> str:
    """Queries the Claude API."""
    if not anthropic_client:
        return "Claude API key not configured or client initialization failed."
    try:
        message = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error querying Claude: {e}")
        return "Error: Could not get response from Claude."

def get_mistral_response(question: str) -> str:
    """Queries the Mistral API."""
    if not mistral_client:
        return "Mistral API key not configured or client initialization failed."
    try:
        messages = [
            {"role": "user", "content": question}
        ]
        chat_response = mistral_client.chat(
            model="mistral-large-latest",
            messages=messages,
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error querying Mistral: {e}")
        return "Error: Could not get response from Mistral."

def get_gemini_response(question: str) -> str:
    """Queries the Gemini API."""
    if not gemini_model:
        return "Gemini API key not configured or client initialization failed."
    try:
        response = gemini_model.generate_content(question)
        return response.text
    except Exception as e:
        print(f"Error querying Gemini: {e}")
        return "Error: Could not get response from Gemini."

def get_grok_response(question: str) -> str:
    """Queries the Grok API using a direct REST call."""
    if not GROK_API_KEY:
        return "Grok API key not configured."

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "grok-1",
        "messages": [
            {"role": "user", "content": question}
        ],
    }

    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error querying Grok: {e}")
        return "Error: Could not get response from Grok."
    except (KeyError, IndexError) as e:
        print(f"Error parsing Grok response: {e}")
        return "Error: Invalid response format from Grok."

def get_deepseek_response(question: str) -> str:
    """Queries the Deepseek API."""
    if not deepseek_client:
        return "Deepseek API key not configured or client initialization failed."
    try:
        completion = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error querying Deepseek: {e}")
        return f"Error: Could not get response from Deepseek."


LLM_PROVIDERS = {
    "chatgpt": get_chatgpt_response,
    "claude": get_claude_response,
    "mistral": get_mistral_response,
    "gemini": get_gemini_response,
    "grok": get_grok_response,
    "deepseek": get_deepseek_response,
}
