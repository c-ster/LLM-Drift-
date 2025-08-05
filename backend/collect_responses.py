import sqlite3
import openai
import anthropic
import cohere
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import Config

class LLMCollector:
    def __init__(self):
        self.config = Config
        self._setup_clients()
        
    def _setup_clients(self):
        """Initialize API clients for different LLM providers."""
        # Initialize OpenAI client
        if self.config.OPENAI_API_KEY:
            openai.api_key = self.config.OPENAI_API_KEY
            
        # Initialize Anthropic client
        self.anthropic_client = None
        if self.config.ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
            
        # Initialize Cohere client
        self.cohere_client = None
        if self.config.COHERE_API_KEY:
            self.cohere_client = cohere.Client(self.config.COHERE_API_KEY)
    
    def get_db_connection(self):
        """Create a database connection."""
        return sqlite3.connect(self.config.DATABASE_URL)
    
    def ensure_llm_model(self, model_name: str, provider: str, version: str = None) -> int:
        """Ensure the LLM model exists in the database and return its ID."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO llm_models (name, provider, version) VALUES (?, ?, ?)',
                (model_name, provider, version)
            )
            if cursor.lastrowid == 0:
                cursor.execute(
                    'SELECT id FROM llm_models WHERE name = ?',
                    (model_name,)
                )
                return cursor.fetchone()[0]
            return cursor.lastrowid
    
    def ensure_question(self, question_text: str, category: str = None) -> int:
        """Ensure the question exists in the database and return its ID."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO questions (question_text, category) VALUES (?, ?)',
                (question_text, category)
            )
            if cursor.lastrowid == 0:
                cursor.execute(
                    'SELECT id FROM questions WHERE question_text = ?',
                    (question_text,)
                )
                return cursor.fetchone()[0]
            return cursor.lastrowid
    
    def save_response(self, llm_id: int, question_id: int, response_text: str, 
                     prompt_tokens: int = None, completion_tokens: int = None, 
                     total_tokens: int = None, temperature: float = 0.7) -> None:
        """Save the LLM response to the database."""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO responses 
                (llm_id, question_id, response_text, prompt_tokens, completion_tokens, total_tokens, temperature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (llm_id, question_id, response_text, prompt_tokens, 
                 completion_tokens, total_tokens, temperature)
            )
    
    def query_openai(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query OpenAI's API."""
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return {
            'text': response.choices[0].message.content,
            'usage': response.usage,
            'model': model
        }
    
    def query_anthropic(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query Anthropic's API."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Check your API key.")
            
        response = self.anthropic_client.completions.create(
            model=model,
            prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
            **kwargs
        )
        return {
            'text': response.completion,
            'usage': {
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            },
            'model': model
        }
    
    def query_cohere(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Query Cohere's API."""
        if not self.cohere_client:
            raise ValueError("Cohere client not initialized. Check your API key.")
            
        response = self.cohere_client.generate(
            model=model,
            prompt=prompt,
            **kwargs
        )
        return {
            'text': response.generations[0].text,
            'usage': {
                'prompt_tokens': response.meta.tokens.prompt_tokens,
                'completion_tokens': response.meta.tokens.response_tokens,
                'total_tokens': response.meta.tokens.total_tokens
            },
            'model': model
        }
    
    def collect_responses(self, questions: List[str] = None):
        """Collect responses for all configured questions from all LLMs."""
        questions = questions or self.config.QUESTIONS
        
        for question in questions:
            question_id = self.ensure_question(question)
            
            for model_name, model_config in self.config.LLM_CONFIGS.items():
                provider = model_config['provider']
                model = model_config['model']
                temperature = model_config.get('temperature', 0.7)
                max_tokens = model_config.get('max_tokens', 1000)
                
                print(f"Querying {model_name} for: {question[:50]}...")
                
                try:
                    # Get LLM model ID
                    llm_id = self.ensure_llm_model(model_name, provider, model)
                    
                    # Query the appropriate API
                    if provider == 'openai':
                        response = self.query_openai(
                            model=model,
                            prompt=question,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    elif provider == 'anthropic':
                        response = self.query_anthropic(
                            model=model,
                            prompt=question,
                            temperature=temperature,
                            max_tokens_to_sample=max_tokens
                        )
                    elif provider == 'cohere':
                        response = self.query_cohere(
                            model=model,
                            prompt=question,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    else:
                        print(f"Unsupported provider: {provider}")
                        continue
                    
                    # Save the response
                    self.save_response(
                        llm_id=llm_id,
                        question_id=question_id,
                        response_text=response['text'],
                        prompt_tokens=response['usage'].get('prompt_tokens'),
                        completion_tokens=response['usage'].get('completion_tokens'),
                        total_tokens=response['usage'].get('total_tokens'),
                        temperature=temperature
                    )
                    
                    print(f"Successfully collected response from {model_name}")
                    
                except Exception as e:
                    print(f"Error querying {model_name}: {str(e)}")
                
                # Be nice to the APIs
                time.sleep(1)

def main():
    # Initialize the database if it doesn't exist
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Create collector instance
    collector = LLMCollector()
    
    # Collect responses
    collector.collect_responses()
    
    print("Response collection complete!")

if __name__ == "__main__":
    main()
