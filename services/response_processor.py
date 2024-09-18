import json
import re

from logger import Logger

class ResponseProcessor:
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_json(self, response):
        try:
            extracted_json = self._extract_json(response)
            return json.loads(extracted_json)
        except json.JSONDecodeError as e:
            self.logger.log_error(f"Extracted content is not valid JSON. Error: {e}. Raw response: {response}")
            raise ValueError("Extracted content is not valid JSON.")

    def process(self, responses):
        full_response = ""

        for line in responses.iter_lines():
            if line:
                full_response += self.get_response_part(line)

        return full_response

    def get_response_part(self, line):
        try:
            return json.loads(line).get('response', "")
        except json.JSONDecodeError as e:
            self.logger.log_error(f"Error parsing response from Ollama API: {e}. Chunk: {line}")
            raise

    def _extract_json(self, response_text):
        cleaned_response = re.sub(r'```json|```|``|\'\'|[^\x00-\x7F]+', '', response_text, flags=re.DOTALL).strip()

        # Find the first '{' and last '}' to locate the JSON content
        start_index = cleaned_response.find('{')
        end_index = cleaned_response.rfind('}')

        if start_index != -1 and end_index != -1:
            json_content = cleaned_response[start_index:end_index + 1].strip()
            try:
                json.loads(json_content)
                self.logger.log(f"Extracted valid JSON content: {json_content}")
                return json_content
            except json.JSONDecodeError as e:
                self.logger.log_error(f"Extracted content is not valid JSON: {json_content}. Error: {e}")
                raise ValueError("Extracted content is not valid JSON.")
        else:
            self.logger.log_error(f"Could not find valid JSON structure in the response: {response_text}")
            raise ValueError("No valid JSON found in the response.")
