#!/usr/bin/env python3
"""
LLM Drift Monitor - Scheduled Job Runner

This script runs the LLM response collection on a schedule.
"""
import time
import logging
from datetime import datetime
from collect_responses import LLMCollector
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_collection():
    """Run a single collection of responses."""
    try:
        logger.info("Starting LLM response collection...")
        collector = LLMCollector()
        collector.collect_responses()
        logger.info("LLM response collection completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error during collection: {str(e)}", exc_info=True)
        return False

def main():
    """Main entry point for the scheduled job."""
    logger.info("LLM Drift Monitor started")
    
    # Run immediately on start
    run_collection()
    
    # Then run on the configured schedule
    while True:
        try:
            # Calculate sleep time until next interval
            now = datetime.now()
            next_run = now.replace(hour=0, minute=0, second=0, microsecond=0) \
                     + timedelta(days=1)  # Run daily at midnight
            
            if next_run < now:  # If next run is in the past, skip to next day
                next_run += timedelta(days=1)
            
            sleep_seconds = (next_run - now).total_seconds()
            logger.info(f"Next collection scheduled for {next_run} (in {sleep_seconds/3600:.1f} hours)")
            
            # Sleep until next run time
            time.sleep(sleep_seconds)
            
            # Run collection
            run_collection()
            
        except KeyboardInterrupt:
            logger.info("Shutting down LLM Drift Monitor...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            # Wait a bit before retrying on error
            time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    from datetime import timedelta  # Moved here to avoid circular import
    main()
