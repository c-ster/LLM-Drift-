import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TestConfig:
    # Database configuration
    DATABASE_URL = 'data/test_llm_responses.db'
    
    # Test with just one question to minimize API calls
    QUESTIONS = [
        "What are the ethical implications of AI in healthcare?"
    ]
    
    # Test with just one model to minimize API calls
    LLM_CONFIGS = {
        'gpt-3.5-turbo': {
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 100
        }
    }
