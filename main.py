import os
import sys

from fastapi import HTTPException, FastAPI

from file_loader import FileLoader
from logger import Logger
from paperless_post_processor import PaperlessPostProcessor
from services.ollama_service import OllamaService
from services.paperless_service import PaperlessService


def validate_env_vars():
    # Required environment variables (no default, must be set)
    required_env_vars = [
        'PAPERLESS_API_TOKEN'
    ]

    # Optional environment variables with default values
    optional_env_vars_with_defaults = {
        'APP_PORT': '5000',
        'LOG_FILE': '/data/log',
        'OLLAMA_PROMPT_FILE': '/data/prompt',
        'OLLAMA_MODEL_NAME': 'gemma2:2b',
        'OLLAMA_API_URL': 'http://ollama:11434/api/generate',
        'OLLAMA_TRUNCATE_NUMBER': '200',
        'PAPERLESS_API_URL': 'http://paperless-ngx:8000/api'
    }

    # Check if required variables are set
    for var in required_env_vars:
        if not os.getenv(var):
            raise RuntimeError(f"Required environment variable {var} is not set.")

    # Check optional variables and use default if not set
    for var, default_value in optional_env_vars_with_defaults.items():
        if not os.getenv(var):
            print(f"{var} is not set. Defaulting to {default_value}.")
            os.environ[var] = default_value  # Set the default in the environment

    # Additional validation for numeric values
    app_port = os.getenv('APP_PORT')
    if not app_port.isdigit() or not (0 <= int(app_port) <= 65535):
        raise RuntimeError("APP_PORT must be a valid integer between 0 and 65535.")

    truncate_number = os.getenv('OLLAMA_TRUNCATE_NUMBER')
    if not truncate_number.isdigit() or int(truncate_number) <= 0:
        raise RuntimeError("OLLAMA_TRUNCATE_NUMBER must be a positive integer.")


# Run validation on startup
validate_env_vars()

# Retrieve environment variables after validation
APP_PORT = int(os.getenv('APP_PORT'))
LOG_FILE = os.getenv('LOG_FILE')
OLLAMA_PROMPT_FILE = os.getenv('OLLAMA_PROMPT_FILE')
OLLAMA_MODEL_NAME = os.getenv('OLLAMA_MODEL_NAME')
OLLAMA_API_URL = os.getenv('OLLAMA_API_URL')
OLLAMA_TRUNCATE_NUMBER = int(os.getenv('OLLAMA_TRUNCATE_NUMBER'))
PAPERLESS_API_URL = os.getenv('PAPERLESS_API_URL')
PAPERLESS_API_TOKEN = os.getenv('PAPERLESS_API_TOKEN')


app = FastAPI()


@app.get("/")
def read_root():
    return {
        "message": "Environment variables validated successfully",
        "app_port": APP_PORT,
        "log_file": LOG_FILE,
        "ollama_prompt_file": OLLAMA_PROMPT_FILE,
        "ollama_model_name": OLLAMA_MODEL_NAME,
        "ollama_api_url": OLLAMA_API_URL,
        "ollama_truncate_number": OLLAMA_TRUNCATE_NUMBER,
        "paperless_api_url": PAPERLESS_API_URL,
        "paperless_api_token": PAPERLESS_API_TOKEN,
    }


@app.get("/process/{doc_id}")
async def process(doc_id: int):
    logger = Logger(LOG_FILE)
    file_loader = FileLoader()

    if doc_id is None:
        logger.log("No document ID provided. Exiting.")
        sys.exit(1)

    paperless = PaperlessService(logger, PAPERLESS_API_URL, PAPERLESS_API_TOKEN)
    ollama = OllamaService(logger, OLLAMA_API_URL, OLLAMA_PROMPT_FILE, OLLAMA_MODEL_NAME, OLLAMA_TRUNCATE_NUMBER, file_loader)

    try:
        processor = PaperlessPostProcessor(logger, paperless, ollama)
        processor.process_document(doc_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
