import unittest
from unittest.mock import patch, MagicMock
from models.postprocessed_document import PostProcessedDocument
from services.paperless.document_service import DocumentService


class TestDocumentService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.doc_service = DocumentService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.paperless.document_service.DocumentReader.get_document')
    def test_get_document_success(self, mock_get_document):
        # given
        mock_get_document.return_value = {
            'id': 1,
            'title': 'Test Document',
            'created_date': '2023-09-18',
            'content': 'This is the document content',
            'correspondent': 2,
            'document_type': 3,
            'tags': [1, 2, 3]
        }

        # when
        document = self.doc_service.get_document(1)

        # then
        self.assertEqual(document['id'], 1)
        self.assertEqual(document['title'], 'Test Document')
        self.assertEqual(document['created_date'], '2023-09-18')
        mock_get_document.assert_called_once_with(
            1, 'http://api_url/documents/', {'Authorization': 'Token test_token'}
        )

    @patch('services.paperless.document_service.DocumentWriter.update_document')
    def test_update_document_success(self, mock_update_document):
        # given
        mock_update_document.return_value = 200

        post_processed_doc = PostProcessedDocument(
            title='Updated Title',
            created='2024-09-19',
            correspondent=2,
            document_type=3,
            tags=[1, 2, 3]
        )

        # when
        status_code = self.doc_service.update_document(1, post_processed_doc)

        # then
        self.assertEqual(status_code, 200)
        mock_update_document.assert_called_once_with(
            1, post_processed_doc, 'http://api_url/documents/', {'Authorization': 'Token test_token'}
        )

    @patch('services.paperless.document_service.DocumentReader.get_document')
    def test_get_document_failure(self, mock_get_document):
        # given
        mock_get_document.side_effect = ValueError("Document not found")

        # when / then
        with self.assertRaises(ValueError) as context:
            self.doc_service.get_document(999)

        self.assertEqual(str(context.exception), "Document not found")
        mock_get_document.assert_called_once_with(
            999, 'http://api_url/documents/', {'Authorization': 'Token test_token'}
        )

    @patch('services.paperless.document_service.DocumentWriter.update_document')
    def test_update_document_failure(self, mock_update_document):
        # given
        mock_update_document.side_effect = Exception("Failed to update document")

        post_processed_doc = PostProcessedDocument(
            title='Failed Update',
            created=None,
            correspondent=None,
            document_type=None,
            tags=[]
        )

        # when / then
        with self.assertRaises(Exception) as context:
            self.doc_service.update_document(1, post_processed_doc)

        self.assertEqual(str(context.exception), "Failed to update document")
        mock_update_document.assert_called_once_with(
            1, post_processed_doc, 'http://api_url/documents/', {'Authorization': 'Token test_token'}
        )


if __name__ == '__main__':
    unittest.main()
