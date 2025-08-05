#!/usr/bin/env python3
"""
Test script for LLM Drift Monitor
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_initialization():
    """Test if the database initializes correctly."""
    print("\n=== Testing Database Initialization ===")
    try:
        # Initialize the test database
        from backend.init_db import init_database
        
        # Remove test database if it exists
        if os.path.exists('data/test_llm_responses.db'):
            os.remove('data/test_llm_responses.db')
        
        # Initialize the database
        init_database()
        
        # Verify the database file was created
        assert os.path.exists('data/test_llm_responses.db'), "Database file was not created"
        
        # Verify tables were created
        conn = sqlite3.connect('data/test_llm_responses.db')
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            AND name IN ('llm_models', 'questions', 'responses')
        """)
        tables = cursor.fetchall()
        assert len(tables) == 3, f"Expected 3 tables, found {len(tables)}"
        
        print("✅ Database initialization test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization test failed: {str(e)}")
        return False

def test_llm_collection():
    """Test collecting responses from LLMs."""
    print("\n=== Testing LLM Response Collection ===")
    try:
        # Import the collector with test config
        import backend.collect_responses as cr
        
        # Replace config with test config
        import backend.test_config
        cr.Config = backend.test_config.TestConfig
        
        # Create a test collector
        collector = cr.LLMCollector()
        
        # Test with a single question
        test_question = "What are the ethical implications of AI in healthcare?"
        
        # Collect responses
        collector.collect_responses([test_question])
        
        # Verify the response was saved
        conn = sqlite3.connect('data/test_llm_responses.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM responses")
        response_count = cursor.fetchone()[0]
        
        assert response_count > 0, "No responses were saved to the database"
        
        print("✅ LLM response collection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ LLM response collection test failed: {str(e)}")
        return False

def test_show_responses():
    """Test the show_responses script."""
    print("\n=== Testing Show Responses ===")
    try:
        # Import the show_responses module
        import backend.show_responses as sr
        
        # Redirect stdout to capture the output
        from io import StringIO
        import sys
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        # Run show_responses
        sr.show_responses()
        
        # Get the output
        output = sys.stdout.getvalue()
        
        # Restore stdout
        sys.stdout = old_stdout
        
        # Check if we got some output
        assert len(output) > 0, "No output from show_responses"
        assert "LLM:" in output, "Expected LLM information in output"
        
        print("✅ Show responses test passed!")
        print("\nSample output:")
        print("-" * 50)
        print(output[:500] + "..." if len(output) > 500 else output)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Show responses test failed: {str(e)}")
        return False

def cleanup():
    """Clean up test files."""
    if os.path.exists('data/test_llm_responses.db'):
        os.remove('data/test_llm_responses.db')
    if os.path.exists('data') and not os.listdir('data'):
        os.rmdir('data')

def main():
    """Run all tests."""
    print("🚀 Starting LLM Drift Monitor Tests")
    print("=" * 50)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run tests
    tests = [
        ("Database Initialization", test_database_initialization),
        ("LLM Response Collection", test_llm_collection),
        ("Show Responses", test_show_responses)
    ]
    
    results = []
    for name, test in tests:
        print(f"\n🔍 Running test: {name}")
        print("-" * 30)
        result = test()
        results.append((name, result))
    
    # Print summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    # Clean up
    cleanup()
    
    # Exit with appropriate code
    if all(result for _, result in results):
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
