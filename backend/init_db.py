import sqlite3
import os

def init_database():
    """Initialize the SQLite database with required tables."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Connect to SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect('data/llm_responses.db')
        cursor = conn.cursor()
        
        # Create tables
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
        
        # Create an index for faster lookups
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_responses_llm_question 
        ON responses(llm_id, question_id, created_at)
        ''')
        
        # Commit changes and close connection
        conn.commit()
        print("Database initialized successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_database()
