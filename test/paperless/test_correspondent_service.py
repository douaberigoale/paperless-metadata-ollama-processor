import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from services.paperless.correspondent_service import CorrespondentService


class TestCorrespondentService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.correspondent_service = CorrespondentService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_all_success(self, mock_get):
        # Given: a successful response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all method is called
        correspondents = self.correspondent_service.get_all()

        # Then: the returned correspondents should match the mock response
        self.assertEqual(len(correspondents), 2)
        self.assertEqual(correspondents[0]['name'], "Correspondent One")
        self.assertEqual(correspondents[1]['name'], "Correspondent Two")

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_all_failure(self, mock_get):
        # Given: a failed request that raises a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("API Failure")

        # When / Then: an exception is raised and the error is logged
        with self.assertRaises(requests.exceptions.RequestException):
            self.correspondent_service.get_all()
        self.mock_logger.log_error.assert_called_once_with("Error fetching correspondents: API Failure")

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_all_names_success(self, mock_get):
        # Given: a successful API response with correspondent names
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all_names method is called
        correspondent_names = self.correspondent_service.get_all_names()

        # Then: the correspondent names should be extracted from the response
        self.assertEqual(correspondent_names, ["Correspondent One", "Correspondent Two"])

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_correspondent_name_by_id_success(self, mock_get):
        # Given: a successful API response with multiple correspondents
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_correspondent_name_by_id method is called with a valid ID
        correspondent_name = self.correspondent_service.get_correspondent_name_by_id(2)

        # Then: the correct correspondent name should be returned
        self.assertEqual(correspondent_name, "Correspondent Two")

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_correspondent_name_by_id_not_found(self, mock_get):
        # Given: a successful API response with multiple correspondents
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_correspondent_name_by_id method is called with an invalid ID
        correspondent_name = self.correspondent_service.get_correspondent_name_by_id(999)

        # Then: None should be returned as the correspondent is not found
        self.assertIsNone(correspondent_name)

    # New Tests for Uncovered Methods

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_correspondent_id_by_name_success(self, mock_get):
        # Given: a successful API response with multiple correspondents
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_correspondent_id_by_name method is called with a valid name
        correspondent_id = self.correspondent_service.get_correspondent_id_by_name("Correspondent One")

        # Then: the correct correspondent ID should be returned
        self.assertEqual(correspondent_id, 1)

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_correspondent_id_by_name_case_insensitive(self, mock_get):
        # Given: a successful API response with mixed case correspondent names
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_correspondent_id_by_name method is called with a different case
        correspondent_id = self.correspondent_service.get_correspondent_id_by_name("CORRESPONDENT ONE")

        # Then: the correct correspondent ID should be returned
        self.assertEqual(correspondent_id, 1)

    @patch('services.paperless.correspondent_service.requests.get')
    def test_get_correspondent_id_by_name_not_found(self, mock_get):
        # Given: a successful API response with multiple correspondents
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Correspondent One"},
                {"id": 2, "name": "Correspondent Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_correspondent_id_by_name method is called with an invalid name
        correspondent_id = self.correspondent_service.get_correspondent_id_by_name("Invalid Correspondent")

        # Then: None should be returned as the correspondent is not found
        self.assertIsNone(correspondent_id)

    @patch('services.paperless.correspondent_service.requests.post')
    def test_create_correspondent_success(self, mock_post):
        # Given: a successful POST response for creating a new correspondent
        mock_response = Mock()
        mock_response.json.return_value = {"id": 3}
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # When: the create_correspondent method is called
        new_correspondent_id = self.correspondent_service.create_correspondent("New Correspondent")

        # Then: the ID of the newly created correspondent should be returned
        self.assertEqual(new_correspondent_id, 3)

    @patch('services.paperless.correspondent_service.requests.post')
    def test_create_correspondent_failure(self, mock_post):
        # Given: a failed POST request
        mock_post.side_effect = requests.exceptions.RequestException("API Failure")

        # When / Then: an exception is raised and the error is logged
        with self.assertRaises(requests.exceptions.RequestException):
            self.correspondent_service.create_correspondent("New Correspondent")
        self.mock_logger.log_error.assert_called_once_with("Error creating correspondent 'New Correspondent': API Failure")

    @patch('services.paperless.correspondent_service.requests.post')
    def test_create_correspondent_already_exists(self, mock_post):
        # Given: a successful POST response that indicates the correspondent already exists
        mock_response = Mock()
        mock_response.json.return_value = {"id": 1}
        mock_response.status_code = 200  # Assuming the API returns 200 for already existing
        mock_post.return_value = mock_response

        # When: the create_correspondent method is called for an existing correspondent
        correspondent_id = self.correspondent_service.create_correspondent("Correspondent One")

        # Then: the existing ID should be returned without errors
        self.assertEqual(correspondent_id, 1)


if __name__ == '__main__':
    unittest.main()
