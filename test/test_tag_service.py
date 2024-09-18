import unittest
from unittest.mock import patch, Mock, MagicMock
import requests
from services.tag_service import TagService


class TestTagService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.tag_service = TagService(self.mock_logger, 'http://api_url', 'test_token')

    @patch('services.tag_service.requests.get')  # Patch the correct module path
    def test_get_all_tags_success(self, mock_get):
        # Given: a successful response from the API
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all method is called
        tags = self.tag_service.get_all()

        # Then: the returned tags should match the mock response
        self.assertEqual(len(tags), 2)
        self.assertEqual(tags[0]['name'], "Tag One")
        self.assertEqual(tags[1]['name'], "Tag Two")

    @patch('services.tag_service.requests.get')
    def test_get_all_tags_failure(self, mock_get):
        # Given: a failed request that raises a RequestException
        mock_get.side_effect = requests.exceptions.RequestException("API Failure")

        # When / Then: an exception is raised and the error is logged
        with self.assertRaises(requests.exceptions.RequestException):
            self.tag_service.get_all()
        self.mock_logger.log_error.assert_called_once_with("Error fetching tags: API Failure")

    @patch('services.tag_service.requests.get')
    def test_get_all_tag_names_success(self, mock_get):
        # Given: a successful API response with tag names
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_all_names method is called
        tag_names = self.tag_service.get_all_names()

        # Then: the tag names should be extracted from the response
        self.assertEqual(tag_names, ["Tag One", "Tag Two"])

    @patch('services.tag_service.requests.get')
    def test_get_tag_name_by_id_success(self, mock_get):
        # Given: a successful API response with multiple tags
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_tag_name_by_id method is called with a valid ID
        tag_name = self.tag_service.get_tag_names_by_ids([2])

        # Then: the correct tag name should be returned
        self.assertEqual(tag_name[0], "Tag Two")

    @patch('services.tag_service.requests.get')
    def test_get_tag_name_by_id_not_found(self, mock_get):
        # Given: a successful API response with multiple tags
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_tag_name_by_id method is called with an invalid ID
        tag_name = self.tag_service.get_tag_names_by_ids([999])

        # Then: None should be returned as the tag is not found
        self.assertEqual(tag_name, [])

    # New Tests for Uncovered Methods

    @patch('services.tag_service.requests.get')
    def test_get_tag_ids_by_names_success(self, mock_get):
        # Given: a successful API response with multiple tags
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_tag_ids_by_names method is called with valid names
        tag_ids = self.tag_service.get_tag_ids_by_names(["Tag One", "Tag Two"])

        # Then: the correct tag IDs should be returned
        self.assertEqual(tag_ids, [1, 2])

    @patch('services.tag_service.requests.get')
    def test_get_tag_ids_by_names_partial_success(self, mock_get):
        # Given: a successful API response with some matching tag names
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "name": "Tag One"},
                {"id": 2, "name": "Tag Two"}
            ]
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # When: the get_tag_ids_by_names method is called with one valid and one invalid name
        tag_ids = self.tag_service.get_tag_ids_by_names(["Tag One", "Nonexistent Tag"])

        # Then: only the valid tag ID should be returned
        self.assertEqual(tag_ids, [1])

    @patch('services.tag_service.requests.post')
    def test_create_tags_success(self, mock_post):
        # Given: a successful POST request for creating a new tag
        mock_response = Mock()
        mock_response.json.return_value = {"id": 3}
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # When: the create_tags method is called
        new_tag_ids = self.tag_service.create_tags(["New Tag"])

        # Then: the ID of the newly created tag should be returned
        self.assertEqual(new_tag_ids, [3])

    @patch('services.tag_service.requests.post')
    def test_create_tags_failure(self, mock_post):
        # Given: a failed POST request
        mock_post.side_effect = requests.exceptions.RequestException("API Failure")

        # When / Then: an exception is raised and the error is logged
        with self.assertRaises(requests.exceptions.RequestException):
            self.tag_service.create_tags(["New Tag"])
        self.mock_logger.log_error.assert_called_once_with("Error creating tag 'New Tag': API Failure")


if __name__ == '__main__':
    unittest.main()
