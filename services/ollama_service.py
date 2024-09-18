import json
import requests

from logger import Logger
from models.extracted_metadata import ExtractedMetadata
from services.prompt_creator import PromptCreator
from services.response_processor import ResponseProcessor


class OllamaService:
    def __init__(self,
                 logger: Logger,
                 api_url,
                 model_name,
                 prompt_creator: PromptCreator,
                 response_processor: ResponseProcessor):
        self.logger = logger
        self.api_url = api_url
        self.model_name = model_name
        self.prompt_creator = prompt_creator
        self.response_processor = response_processor

        if not self.model_name:
            raise ValueError("Environment variable 'OLLAMA_MODEL_NAME' is not set or empty")

    def extract_metadata(self, ocr_text):
        data = {
            "model": self.model_name,
            "prompt": self.prompt_creator.create_prompt(ocr_text)
        }

        try:
            responses = requests.post(self.api_url, json=data, stream=True)
            complete_response = self.response_processor.process(responses)
            json_response = self.response_processor.get_json(complete_response)

            if not json_response:
                self.logger.log_error("Received empty or invalid JSON from Ollama API.")
                self.logger.log_error(f"Failed data: {data}, Response: {complete_response}")
                raise ValueError(f"Invalid JSON response from Ollama API: {complete_response}")

            metadata = ExtractedMetadata(
                title=json_response.get('title'),
                created_date=json_response.get('date'),
                correspondent=json_response.get('correspondent'),
                document_type=json_response.get('document_type'),
                tags=json_response.get('tags', [])
            )

            return metadata

        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"HTTP error calling Ollama API: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.log_error(f"Error parsing responses from Ollama API: {e}.")
            self.logger.log_error(f"Failed data: {data}, Raw response: {complete_response}")
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error calling Ollama API: {e}")
            raise
