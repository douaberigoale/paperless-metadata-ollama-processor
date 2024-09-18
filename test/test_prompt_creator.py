import unittest
from unittest.mock import MagicMock

from services.prompt_creator import PromptCreator


class TestPromptCreator(unittest.TestCase):

    def setUp(self):
        # Given: a PromptCreator with mocked services and logger
        self.mock_logger = MagicMock()
        self.mock_file_loader = MagicMock()
        self.mock_tag_service = MagicMock()
        self.mock_correspondent_service = MagicMock()
        self.mock_document_type_service = MagicMock()

        self.prompt_creator = PromptCreator(
            logger=self.mock_logger,
            prompt_file_path='path/to/prompt_file.txt',
            truncate_number=100,
            file_loader=self.mock_file_loader,
            tag_service=self.mock_tag_service,
            correspondent_service=self.mock_correspondent_service,
            document_type_service=self.mock_document_type_service
        )

    def test_create_prompt_success(self):
        # Given: mock data for tags, correspondents, document types, and prompt template
        self.mock_tag_service.get_all_names.return_value = ["Tag1", "Tag2"]
        self.mock_correspondent_service.get_all_names.return_value = ["Correspondent1", "Correspondent2"]
        self.mock_document_type_service.get_all_names.return_value = ["Type1", "Type2"]
        self.mock_file_loader.load.return_value = (
            "OCR Text: {truncated_text}\n"
            "Tags: {existing_tags}\n"
            "Correspondents: {existing_correspondents}\n"
            "Types: {existing_types}\n"
        )

        # When: create_prompt is called with OCR text
        ocr_text = "This is a sample OCR text with more than enough words to truncate."
        prompt = self.prompt_creator.create_prompt(ocr_text)

        # Then: the prompt should be formatted correctly
        expected_prompt = (
            "OCR Text: This is a sample OCR text with more than enough words to truncate.\n"
            "Tags: Tag1, Tag2\n"
            "Correspondents: Correspondent1, Correspondent2\n"
            "Types: Type1, Type2\n"
        )
        self.assertEqual(prompt, expected_prompt)

    def test_create_prompt_truncated_text(self):
        # Given: mock services and template, truncate text to 5 words
        self.prompt_creator.truncate_number = 5
        self.mock_tag_service.get_all_names.return_value = ["Tag1", "Tag2"]
        self.mock_correspondent_service.get_all_names.return_value = ["Correspondent1", "Correspondent2"]
        self.mock_document_type_service.get_all_names.return_value = ["Type1", "Type2"]
        self.mock_file_loader.load.return_value = (
            "OCR Text: {truncated_text}\n"
            "Tags: {existing_tags}\n"
            "Correspondents: {existing_correspondents}\n"
            "Types: {existing_types}\n"
        )

        # When: create_prompt is called with long OCR text
        ocr_text = "This is a sample OCR text with many words."
        prompt = self.prompt_creator.create_prompt(ocr_text)

        # Then: the OCR text should be truncated to the first 5 words
        expected_prompt = (
            "OCR Text: This is a sample OCR\n"
            "Tags: Tag1, Tag2\n"
            "Correspondents: Correspondent1, Correspondent2\n"
            "Types: Type1, Type2\n"
        )
        self.assertEqual(prompt, expected_prompt)

    def test_load_prompt_file_empty(self):
        # Given: an empty prompt file that will raise ValueError
        self.mock_file_loader.load.return_value = ""

        # When / Then: _load_prompt should raise ValueError and log the error
        with self.assertRaises(ValueError):
            self.prompt_creator._load_prompt()
        self.mock_logger.log_error.assert_called_once_with("Prompt file is empty or could not be read.")

    def test_missing_prompt_file_path(self):
        # Given: a PromptCreator without a prompt file path
        with self.assertRaises(ValueError):
            PromptCreator(
                logger=self.mock_logger,
                prompt_file_path='',
                truncate_number=100,
                file_loader=self.mock_file_loader,
                tag_service=self.mock_tag_service,
                correspondent_service=self.mock_correspondent_service,
                document_type_service=self.mock_document_type_service
            )


if __name__ == '__main__':
    unittest.main()
