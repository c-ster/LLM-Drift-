import sqlite3

def show_responses():
    try:
        conn = sqlite3.connect('llm_responses.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT llm_name, question, response FROM responses')
        rows = cursor.fetchall()
        
        if not rows:
            print("No responses found in the database.")
            return

        for row in rows:
            llm_name, question, response = row
            print(f"--- LLM: {llm_name} ---")
            print(f"Question: {question}")
            print(f"Response: {response}")
            print("-" * 20)
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    show_responses()
