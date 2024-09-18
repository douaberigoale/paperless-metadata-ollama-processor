import unittest
from unittest.mock import patch, Mock, MagicMock

import requests

from models.document import Document
from models.postprocessed_document import PostProcessedDocument
from services.document_service import DocumentService


class TestDocumentService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.doc_service = DocumentService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.document_service.requests.get')
    def test_get_document_success(self, mock_get):
        # given
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': 1,
            'title': 'Test Document',
            'created_date': '2023-09-18',
            'content': 'This is the document content',
            'correspondent': 2,
            'document_type': 3,
            'tags': [1, 2, 3]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # when
        document = self.doc_service.get_document(1)

        # then
        self.assertIsInstance(document, Document)
        self.assertEqual(document.id, 1)
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.created_date, '2023-09-18')
        self.assertEqual(document.text, 'This is the document content')
        self.assertEqual(document.correspondent_id, 2)
        self.assertEqual(document.document_type_id, 3)
        self.assertEqual(document.tag_ids, [1, 2, 3])

    @patch('services.document_service.requests.get')
    def test_get_document_http_error(self, mock_get):
        # given
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        # when / then
        with self.assertRaises(requests.exceptions.HTTPError):
            self.doc_service.get_document(999)
        self.mock_logger.log_error.assert_called_with("HTTP error: 404 Not Found", unittest.mock.ANY)

    @patch('services.document_service.requests.patch')
    def test_update_document_success(self, mock_patch):
        # given
        mock_response = Mock()
        mock_response.status_code = 200
        mock_patch.return_value = mock_response

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
        mock_patch.assert_called_once_with(
            'http://api_url/documents/1/',
            json={'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3, 'tags': [1, 2, 3]},
            headers={'Authorization': 'Token test_token'}
        )
        self.mock_logger.log.assert_called_once_with(
            "Updating Paperless document with metadata: {'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3, 'tags': [1, 2, 3]}")

    @patch('services.document_service.requests.patch')
    def test_update_document_failure(self, mock_patch):
        # given
        mock_patch.side_effect = Exception("Internal Server Error")

        post_processed_doc = PostProcessedDocument(
            title='Failed Update',
            created=None,
            correspondent=None,
            document_type=None,
            tags=[]
        )

        # when / then
        with self.assertRaises(Exception):
            self.doc_service.update_document(1, post_processed_doc)
        self.mock_logger.log_error.assert_called_once_with(
            "Error updating Paperless document ID 1: Internal Server Error")


if __name__ == '__main__':
    unittest.main()
