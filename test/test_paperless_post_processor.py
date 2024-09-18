import unittest
from unittest.mock import MagicMock, patch
from models.document import Document
from models.extracted_metadata import ExtractedMetadata
from models.postprocessed_document import PostProcessedDocument
from paperless_post_processor import PaperlessPostProcessor


class TestPaperlessPostProcessor(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_document_service = MagicMock()
        self.mock_paperless_service = MagicMock()
        self.mock_ollama_service = MagicMock()

        self.processor = PaperlessPostProcessor(
            logger=self.mock_logger,
            document_service=self.mock_document_service,
            paperless=self.mock_paperless_service,
            ollama=self.mock_ollama_service
        )

        # Sample document and metadata
        self.document = Document(
            id=1, title="Sample Document", created_date="2024-01-01",
            text="This is a sample OCR text", correspondent_id=None, document_type_id=None, tag_ids=[1, 2]
        )

        self.metadata = ExtractedMetadata(
            title="Updated Title", created_date="2024-02-01", correspondent="Test Correspondent",
            document_type="Invoice", tags=["Finance", "Bills"]
        )

        self.post_processed_document = PostProcessedDocument(
            title="Updated Title", created="2024-02-01", correspondent=100, document_type=200, tags=[1, 2]
        )

    def test_process_document_success(self):
        # Given: Document has OCR text and all services succeed
        self.mock_document_service.get_document.return_value = self.document
        self.mock_ollama_service.extract_metadata.return_value = self.metadata
        self.mock_paperless_service.post_process.return_value = self.post_processed_document
        self.mock_document_service.update_document.return_value = MagicMock(status_code=200)

        # When: process_document is called
        self.processor.process_document(1)

        # Then: All service methods should be called correctly
        self.mock_document_service.get_document.assert_called_once_with(1)
        self.mock_ollama_service.extract_metadata.assert_called_once_with(self.document.text)
        self.mock_paperless_service.post_process.assert_called_once_with(self.document, self.metadata)
        self.mock_document_service.update_document.assert_called_once_with(1, self.post_processed_document)

    def test_process_document_no_ocr_text(self):
        # Given: Document has no OCR text
        document_no_text = Document(
            id=1, title="Sample Document", created_date="2024-01-01",
            text="", correspondent_id=None, document_type_id=None, tag_ids=[1, 2]
        )
        self.mock_document_service.get_document.return_value = document_no_text

        # When: process_document is called
        self.processor.process_document(1)

        # Then: The logger should log that no OCR text is found
        self.mock_logger.log.assert_called_once_with("No OCR text found for document ID 1.")
        self.mock_ollama_service.extract_metadata.assert_not_called()
        self.mock_paperless_service.post_process.assert_not_called()
        self.mock_document_service.update_document.assert_not_called()

    def test_process_document_extraction_fails(self):
        # Given: Metadata extraction from Ollama fails
        self.mock_document_service.get_document.return_value = self.document
        self.mock_ollama_service.extract_metadata.side_effect = Exception("Extraction failed")

        # When / Then: process_document raises an exception
        with self.assertRaises(Exception):
            self.processor.process_document(1)

        self.mock_logger.log_error.assert_called_once_with("Error in post-processing document ID 1: Extraction failed")


if __name__ == '__main__':
    unittest.main()
