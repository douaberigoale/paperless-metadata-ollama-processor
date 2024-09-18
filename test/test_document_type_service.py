import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from services.document_type_service import DocumentTypeService

class TestDocumentTypeService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.document_type_service = DocumentTypeService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.document_type_service.requests.get')  # Correct path for patching requests
    def test_get_all_document_types_success(self, mock_get):
        # Given: a successful response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Document Type One"},
                {"id": 2, "name": "Document Type Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all method is called
        document_types = self.document_type_service.get_all()

        # Then: the returned document types should match the mock response
        self.assertEqual(len(document_types), 2)
        self.assertEqual(document_types[0]['name'], "Document Type One")
        self.assertEqual(document_types[1]['name'], "Document Type Two")

    @patch('services.document_type_service.requests.get')
    def test_get_all_document_types_failure(self, mock_get):
        # Given: a failed request that raises a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("API Failure")

        # When / Then: an exception is raised and the error is logged
        with self.assertRaises(requests.exceptions.RequestException):
            self.document_type_service.get_all()
        self.mock_logger.log_error.assert_called_once_with("Error fetching document types: API Failure")

    @patch('services.document_type_service.requests.get')
    def test_get_all_document_type_names_success(self, mock_get):
        # Given: a successful API response with document type names
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Document Type One"},
                {"id": 2, "name": "Document Type Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all_names method is called
        document_type_names = self.document_type_service.get_all_names()

        # Then: the document type names should be extracted from the response
        self.assertEqual(document_type_names, ["Document Type One", "Document Type Two"])

    @patch('services.document_type_service.requests.get')
    def test_get_document_type_name_by_id_success(self, mock_get):
        # Given: a successful API response with multiple document types
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Document Type One"},
                {"id": 2, "name": "Document Type Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_document_type_name_by_id method is called with a valid ID
        document_type_name = self.document_type_service.get_document_type_name_by_id(2)

        # Then: the correct document type name should be returned
        self.assertEqual(document_type_name, "Document Type Two")

    @patch('services.document_type_service.requests.get')
    def test_get_document_type_name_by_id_not_found(self, mock_get):
        # Given: a successful API response with multiple document types
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Document Type One"},
                {"id": 2, "name": "Document Type Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_document_type_name_by_id method is called with an invalid ID
        document_type_name = self.document_type_service.get_document_type_name_by_id(999)

        # Then: None should be returned as the document type is not found
        self.assertIsNone(document_type_name)


if __name__ == '__main__':
    unittest.main()
