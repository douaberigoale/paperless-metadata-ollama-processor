import json
import requests
from logic.Logger import Logger
from logic.FileLoader import FileLoader


class OllamaService:
    def __init__(self, logger: Logger, api_url, prompt_file_path, model_name, truncate_number, file_loader: FileLoader):
        self.logger = logger
        self.file_loader = file_loader
        self.api_url = api_url
        self.prompt_file_path = prompt_file_path
        self.model_name = model_name
        self.truncate_number = truncate_number

        if not self.prompt_file_path:
            raise ValueError("Environment variable 'OLLAMA_PROMPT_FILE' is not set or empty")
        if not self.model_name:
            raise ValueError("Environment variable 'OLLAMA_MODEL_NAME' is not set or empty")

    def load_prompt(self):
        return self.file_loader.load(self.prompt_file_path)

    def call(self, ocr_text, existing_tags, existing_types, existing_correspondents):
        words = ocr_text.split()
        truncated_text = ' '.join(words[:self.truncate_number])

        prompt_template = self.load_prompt()
        prompt = prompt_template.format(
            truncated_text=truncated_text,
            existing_tags=', '.join(existing_tags),
            existing_types=', '.join(existing_types),
            existing_correspondents=', '.join(existing_correspondents)
        )

        data = {
            "model": self.model_name,
            "prompt": prompt
        }

        try:
            response = requests.post(self.api_url, json=data, stream=True)
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    full_response += decoded_line
            return json.loads(full_response)
        except Exception as e:
            self.logger.log_error(f"Error calling Ollama API: {e}")
            raise
