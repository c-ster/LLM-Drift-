# LLM Drift Monitor

Monitor and analyze how responses from different Large Language Models (LLMs) change over time. This tool helps track model drift, compare model outputs, and understand how LLM behavior evolves with different versions and over time.

## Features

- **Multi-LLM Support**: Works with OpenAI, Anthropic, and Cohere models out of the box
- **Scheduled Monitoring**: Automatically collect responses at regular intervals
- **Response Tracking**: Store and compare responses over time
- **Analytics**: Track token usage, response length, and other metrics
- **Extensible**: Easy to add support for additional LLM providers

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LLM-Drift-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**
   - Copy `.env.example` to `.env`
   - Add your API keys for the LLM providers you want to use
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Initialize the database**
   ```bash
   python backend/init_db.py
   ```

## Usage

### Run a single collection
```bash
python backend/collect_responses.py
```

### Run as a scheduled service
```bash
python backend/run_monitor.py
```

### View collected data
```bash
python backend/show_responses.py
```

## Configuration

Edit `backend/config.py` to:
- Add/remove questions
- Configure which models to monitor
- Adjust generation parameters (temperature, max tokens, etc.)

## Data Storage

All data is stored in an SQLite database at `data/llm_responses.db` by default. You can change this in the `.env` file.

## Adding New LLM Providers

1. Add a new method to `LLMCollector` class in `collect_responses.py`
2. Update the `LLM_CONFIGS` in `config.py`
3. Add the required API key to `.env`

## License

MIT License
