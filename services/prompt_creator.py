from file_loader import FileLoader
from logger import Logger
from services.paperless.correspondent_service import CorrespondentService
from services.paperless.document_type_service import DocumentTypeService
from services.paperless.tag_service import TagService


class PromptCreator:
    def __init__(self, logger: Logger, prompt_file_path, truncate_number, file_loader: FileLoader,
                 tag_service: TagService, correspondent_service: CorrespondentService,
                 document_type_service: DocumentTypeService):
        self.logger = logger
        self.file_loader = file_loader
        self.prompt_file_path = prompt_file_path
        self.truncate_number = truncate_number
        self.tag_service = tag_service
        self.correspondent_service = correspondent_service
        self.document_type_service = document_type_service

        if not self.prompt_file_path:
            raise ValueError("Environment variable 'OLLAMA_PROMPT_FILE' is not set or empty")

    def create_prompt(self, ocr_text):
        existing_tags = self.tag_service.get_all_names()
        correspondent_name = self.correspondent_service.get_all_names()
        document_type_name = self.document_type_service.get_all_names()

        words = ocr_text.split()
        truncated_text = ' '.join(words[:self.truncate_number])

        prompt_template = self._load_prompt()

        return prompt_template.format(
            truncated_text=truncated_text,
            existing_tags=self._join_to_string(existing_tags),
            existing_types=self._join_to_string(document_type_name),
            existing_correspondents=self._join_to_string(correspondent_name),
        )

    def _load_prompt(self):
        prompt_content = self.file_loader.load(self.prompt_file_path)
        if not prompt_content:
            self.logger.log_error("Prompt file is empty or could not be read.")
            raise ValueError("Prompt file is empty or could not be read.")
        return prompt_content

    def _join_to_string(self, existing_tags):
        return ', '.join(existing_tags) if existing_tags else ''
