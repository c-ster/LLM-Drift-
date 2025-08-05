import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    DATABASE_URL = 'data/llm_responses.db'
    
    # LLM API configurations
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    
    # LLM configurations
    LLM_CONFIGS = {
        'gpt-4': {
            'provider': 'openai',
            'model': 'gpt-4',
            'temperature': 0.7,
            'max_tokens': 1000
        },
        'claude-2': {
            'provider': 'anthropic',
            'model': 'claude-2',
            'temperature': 0.7,
            'max_tokens': 1000
        },
        'command': {
            'provider': 'cohere',
            'model': 'command',
            'temperature': 0.7,
            'max_tokens': 1000
        }
    }
    
    # Questions to monitor
    QUESTIONS = [
        "What are the ethical implications of AI in healthcare?",
        "How can we ensure AI alignment with human values?",
        "What are the potential risks of artificial general intelligence?",
        "How can we prevent AI from being used for malicious purposes?",
        "What are the economic impacts of widespread AI adoption?"
    ]
    
    # Monitoring schedule (in hours)
    MONITORING_INTERVAL = 24  # Run once per day
