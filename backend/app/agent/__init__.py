import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenRouter client (uses OpenAI-compatible API)
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
        "X-Title": "PM-AI Agent",
    }
)

MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")

def is_agent_enabled() -> bool:
    """Check if OpenRouter API key is configured"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    return bool(api_key) and api_key != "your_key_here"
