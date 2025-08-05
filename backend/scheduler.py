import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal
from . import crud
from . import llm_client
from . import models
from .analysis import calculate_similarity

def load_questions() -> list:
    """Loads questions from the questions.yaml file."""
    try:
        with open("questions.yaml", 'r') as file:
            data = yaml.safe_load(file)
            return data.get('questions', [])
    except FileNotFoundError:
        print("Warning: questions.yaml not found. Using a default question.")
        return ["How did the war in Ukraine and Russia start?"]

def fetch_and_store_responses():
    """Fetches responses from all LLMs for all questions and stores them."""
    db = SessionLocal()
    questions = load_questions()
    if not questions:
        print("No questions to process.")
        return

    try:
        print("--- Starting scheduled LLM query job ---")
        for question in questions:
            print(f"Processing question: {question}")
            for llm_name, query_func in llm_client.LLM_PROVIDERS.items():
                print(f"  Querying {llm_name}...")
                response_text = query_func(question)

                # Find the last response to calculate similarity
                last_response = db.query(models.Response).filter(
                    models.Response.llm_name == llm_name,
                    models.Response.question == question
                ).order_by(models.Response.timestamp.desc()).first()

                similarity_score = None
                if last_response:
                    print(f"  Calculating similarity with previous response...")
                    similarity_score = calculate_similarity(last_response.response, response_text)
                    print(f"  Similarity score: {similarity_score}")

                crud.create_response(
                    db=db, 
                    llm_name=llm_name, 
                    question=question, 
                    response=response_text,
                    similarity_score=similarity_score
                )
                print(f"  Stored response from {llm_name}.")
        print("--- Finished scheduled LLM query job ---")
    finally:
        db.close()

scheduler = BackgroundScheduler()
# Schedule the job to run every 6 hours
scheduler.add_job(fetch_and_store_responses, 'interval', hours=6)

# Run once on startup for immediate data
scheduler.add_job(fetch_and_store_responses, 'date')
