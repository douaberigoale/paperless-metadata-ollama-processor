import unittest
from unittest.mock import MagicMock

from paperless_post_processor import PaperlessPostProcessor
from services.ollama_service import OllamaService
from services.paperless_service import PaperlessService


class TestPaperlessPostProcessor(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.paperless = MagicMock(spec=PaperlessService)
        self.ollama = MagicMock(spec=OllamaService)

        self.processor = PaperlessPostProcessor(self.logger, self.paperless, self.ollama)

    def test_process_document_successful(self):
        # given
        doc_id = 123
        ocr_text = "Sample OCR text"

        self.paperless.get_document_text.return_value = ocr_text
        self.paperless.get_existing_metadata.return_value = (['tag1', 'tag2'], ['type1'], ['correspondent1'])

        metadata = {'tags': ['tag1'], 'types': ['type1'], 'correspondents': ['correspondent1']}
        self.ollama.call.return_value = metadata

        # when
        self.processor.process_document(doc_id)

        # then
        self.paperless.get_document_text.assert_called_once_with(doc_id)
        self.paperless.get_existing_metadata.assert_called_once()

        self.ollama.call.assert_called_once_with(ocr_text, ['tag1', 'tag2'], ['type1'], ['correspondent1'])
        self.paperless.update_document.assert_called_once_with(doc_id, metadata)

    def test_process_document_no_ocr_text(self):
        # given
        doc_id = 123
        self.paperless.get_document_text.return_value = ""

        # when
        self.processor.process_document(doc_id)

        # then
        self.logger.log.assert_called_once_with(f"No OCR text found for document ID {doc_id}.")
        self.paperless.update_document.assert_not_called()

    def test_process_document_exception_in_ocr(self):
        # given
        doc_id = 123
        self.paperless.get_document_text.side_effect = Exception("OCR failure")

        # when
        with self.assertRaises(Exception):
            self.processor.process_document(doc_id)

        # then
        self.logger.log_error.assert_called_once_with(
            f"Error in post-processing document ID {doc_id}: OCR failure")

    def test_process_document_exception_in_metadata_retrieval(self):
        # given
        doc_id = 123
        ocr_text = "Sample OCR text"

        self.paperless.get_document_text.return_value = ocr_text
        self.paperless.get_existing_metadata.side_effect = Exception("Metadata retrieval failure")

        # when
        with self.assertRaises(Exception):
            self.processor.process_document(doc_id)

        # then
        self.logger.log_error.assert_called_once_with(
            f"Error in post-processing document ID {doc_id}: Metadata retrieval failure")

        self.paperless.update_document.assert_not_called()

    def test_process_document_exception_in_ollama(self):
        # given
        doc_id = 123
        ocr_text = "Sample OCR text"

        self.paperless.get_document_text.return_value = ocr_text
        self.paperless.get_existing_metadata.return_value = (['tag1', 'tag2'], ['type1'], ['correspondent1'])
        self.ollama.call.side_effect = Exception("LLM failure")

        # when
        with self.assertRaises(Exception):
            self.processor.process_document(doc_id)

        # then
        self.logger.log_error.assert_called_once_with(
            f"Error in post-processing document ID {doc_id}: LLM failure")

        self.paperless.update_document.assert_not_called()

    def test_process_document_exception_in_update_document(self):
        # given
        doc_id = 123
        ocr_text = "Sample OCR text"

        self.paperless.get_document_text.return_value = ocr_text
        self.paperless.get_existing_metadata.return_value = (['tag1', 'tag2'], ['type1'], ['correspondent1'])

        metadata = {'tags': ['tag1'], 'types': ['type1'], 'correspondents': ['correspondent1']}
        self.ollama.call.return_value = metadata

        self.paperless.update_document.side_effect = Exception("Update failure")

        # when
        with self.assertRaises(Exception):
            self.processor.process_document(doc_id)

        # then
        self.logger.log_error.assert_called_once_with(
            f"Error in post-processing document ID {doc_id}: Update failure")

    def test_process_document_successful_update_response(self):
        # given
        doc_id = 123
        ocr_text = "Sample OCR text"

        self.paperless.get_document_text.return_value = ocr_text
        self.paperless.get_existing_metadata.return_value = (['tag1', 'tag2'], ['type1'], ['correspondent1'])

        metadata = {'tags': ['tag1'], 'types': ['type1'], 'correspondents': ['correspondent1']}
        self.ollama.call.return_value = metadata

        self.paperless.update_document.return_value = 200

        # when
        self.processor.process_document(doc_id)

        # then
        self.paperless.update_document.assert_called_once_with(doc_id, metadata)


if __name__ == '__main__':
    unittest.main()
