import unittest
from unittest.mock import patch, Mock, MagicMock
from models.postprocessed_document import PostProcessedDocument
from services.paperless.document_writer import DocumentWriter


class TestDocumentWriter(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.doc_service = DocumentWriter(self.mock_logger)

    @patch('services.paperless.document_writer.requests.patch')
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
        status_code = self.doc_service.update_document(1, post_processed_doc, "http://api_url/documents/", "")

        # then
        self.assertEqual(status_code, 200)
        mock_patch.assert_called_once_with(
            'http://api_url/documents/1/',
            json={'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3,
                  'tags': [1, 2, 3]},
            headers=""
        )
        self.mock_logger.log.assert_called_once_with(
            "Updating Paperless document with metadata: {'title': 'Updated Title', 'created': '2024-09-19', 'correspondent': 2, 'document_type': 3, 'tags': [1, 2, 3]}")

    @patch('services.paperless.document_writer.requests.patch')
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
        with self.assertRaises(Exception) as context:
            self.doc_service.update_document(1, post_processed_doc, "", "")

        # assert
        self.assertEqual(str(context.exception), "Internal Server Error")

        # assert
        self.mock_logger.log_error.assert_called_once_with(
            "Unexpected error updating document ID 1: Internal Server Error"
        )


if __name__ == '__main__':
    unittest.main()
