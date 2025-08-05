#!/usr/bin/env python3
"""
Mock LLM Collector for Testing
"""
import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockLLMCollector:
    """Mock version of the LLM collector for testing."""
    
    def __init__(self):
        self.db_path = 'data/test_llm_responses.db'
        self._setup_database()
        
    def _setup_database(self):
        """Set up the test database."""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS llm_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            provider TEXT NOT NULL,
            version TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_text TEXT NOT NULL UNIQUE,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            llm_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            response_text TEXT NOT NULL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER,
            temperature REAL DEFAULT 0.7,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (llm_id) REFERENCES llm_models (id),
            FOREIGN KEY (question_id) REFERENCES questions (id),
            UNIQUE(llm_id, question_id, created_at)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_mock_response(self, question: str, model_name: str) -> Dict[str, Any]:
        """Generate a mock response for testing."""
        responses = {
            "gpt-3.5-turbo": {
                "text": f"This is a mock response from {model_name} to: {question}",
                "usage": {
                    "prompt_tokens": len(question.split()),
                    "completion_tokens": 50,
                    "total_tokens": len(question.split()) + 50
                }
            },
            "claude-2": {
                "text": f"Mock Claude response to: {question}",
                "usage": {
                    "prompt_tokens": len(question.split()),
                    "completion_tokens": 45,
                    "total_tokens": len(question.split()) + 45
                }
            },
            "command": {
                "text": f"Mock Cohere response to: {question}",
                "usage": {
                    "prompt_tokens": len(question.split()),
                    "completion_tokens": 40,
                    "total_tokens": len(question.split()) + 40
                }
            }
        }
        return responses.get(model_name, responses["gpt-3.5-turbo"])
    
    def collect_responses(self, questions: List[str] = None):
        """Collect mock responses for the given questions."""
        if questions is None:
            questions = ["What are the ethical implications of AI in healthcare?"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ensure models exist
        models = [
            ("gpt-3.5-turbo", "openai", None),
            ("claude-2", "anthropic", None),
            ("command", "cohere", None)
        ]
        
        model_ids = {}
        for name, provider, version in models:
            cursor.execute(
                'INSERT OR IGNORE INTO llm_models (name, provider, version) VALUES (?, ?, ?)',
                (name, provider, version)
            )
            if cursor.lastrowid == 0:
                cursor.execute('SELECT id FROM llm_models WHERE name = ?', (name,))
                model_ids[name] = cursor.fetchone()[0]
            else:
                model_ids[name] = cursor.lastrowid
        
        # Process each question
        for question in questions:
            # Ensure question exists
            cursor.execute(
                'INSERT OR IGNORE INTO questions (question_text) VALUES (?)',
                (question,)
            )
            if cursor.lastrowid == 0:
                cursor.execute('SELECT id FROM questions WHERE question_text = ?', (question,))
                question_id = cursor.fetchone()[0]
            else:
                question_id = cursor.lastrowid
            
            # Generate mock response for each model
            for model_name in model_ids:
                response = self._get_mock_response(question, model_name)
                
                # Save response
                cursor.execute(
                    '''
                    INSERT INTO responses 
                    (llm_id, question_id, response_text, prompt_tokens, completion_tokens, total_tokens)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        model_ids[model_name],
                        question_id,
                        response['text'],
                        response['usage']['prompt_tokens'],
                        response['usage']['completion_tokens'],
                        response['usage']['total_tokens']
                    )
                )
        
        conn.commit()
        conn.close()
        print("✅ Mock responses collected successfully!")

def test_mock_collector():
    """Test the mock collector."""
    print("🚀 Testing Mock LLM Collector")
    print("=" * 50)
    
    # Initialize the collector
    collector = MockLLMCollector()
    
    # Test with a sample question
    test_question = "What are the ethical implications of AI in healthcare?"
    print(f"\n📝 Testing with question: {test_question}")
    
    # Collect mock responses
    collector.collect_responses([test_question])
    
    # Verify the data was saved
    conn = sqlite3.connect('data/test_llm_responses.db')
    cursor = conn.cursor()
    
    # Check if we have responses
    cursor.execute('''
        SELECT m.name, q.question_text, r.response_text, r.created_at
        FROM responses r
        JOIN llm_models m ON r.llm_id = m.id
        JOIN questions q ON r.question_id = q.id
        ORDER BY m.name
    ''')
    
    print("\n📊 Stored Responses:")
    print("-" * 80)
    for row in cursor.fetchall():
        model, question, response, timestamp = row
        print(f"Model: {model}")
        print(f"Question: {question}")
        print(f"Response: {response[:100]}...")
        print(f"Timestamp: {timestamp}")
        print("-" * 80)
    
    conn.close()
    
    print("\n🎉 Mock collector test completed successfully!")

if __name__ == "__main__":
    test_mock_collector()
