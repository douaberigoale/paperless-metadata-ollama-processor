import unittest
from unittest.mock import MagicMock
from services.paperless_service import PaperlessService
from models.document import Document
from models.extracted_metadata import ExtractedMetadata


class TestPaperlessService(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.mock_document_service = MagicMock()
        self.mock_tag_service = MagicMock()
        self.mock_correspondent_service = MagicMock()
        self.mock_document_type_service = MagicMock()

        self.paperless_service = PaperlessService(logger=self.mock_logger, tag_service=self.mock_tag_service,
                                                  correspondent_service=self.mock_correspondent_service,
                                                  document_type_service=self.mock_document_type_service)

        self.document = Document(
            id=1, title="Test Document", created_date="2024-01-01",
            text="Sample content", correspondent_id=None, document_type_id=None, tag_ids=[1, 2]
        )

        self.metadata = ExtractedMetadata(
            title="Updated Title", created_date="2024-02-01", correspondent="Test Correspondent",
            document_type="Invoice", tags=["Finance", "Bills"]
        )

    def test_get_tag_ids_no_existing_tags_creates_new(self):
        # Given: Document has no tags, new tags found in metadata
        self.mock_tag_service.get_tag_names_by_ids.return_value = []
        self.mock_tag_service.get_tag_ids_by_names.return_value = []
        self.mock_tag_service.create_tags.return_value = [1, 2]

        # When: get_tag_ids is called
        tag_ids = self.paperless_service.get_tag_ids([], ["Finance", "Bills"])

        # Then: All tags should be created and returned
        self.assertEqual(tag_ids, [1, 2])

    def test_get_tag_ids_existing_no_new_tags(self):
        # Given: Document has tags, no new tags in metadata
        self.mock_tag_service.get_tag_names_by_ids.return_value = ["Finance"]
        self.mock_tag_service.get_tag_ids_by_names.return_value = [1]
        self.mock_tag_service.create_tags.return_value = []  # Ensure this is an empty list

        # When: get_tag_ids is called
        tag_ids = self.paperless_service.get_tag_ids([1], ["Finance"])

        # Then: Only existing tags should be returned
        self.assertEqual(tag_ids, [1])

    def test_get_tag_ids_existing_and_new_tags(self):
        # Given: Document has existing tags, new tags found in metadata
        self.mock_tag_service.get_tag_names_by_ids.return_value = ["Finance"]
        self.mock_tag_service.get_tag_ids_by_names.return_value = [1]
        self.mock_tag_service.create_tags.return_value = [3]

        # When: get_tag_ids is called
        tag_ids = self.paperless_service.get_tag_ids([1], ["Finance", "Bills"])

        # Then: Both existing and new tag IDs should be returned
        self.assertEqual(tag_ids, [1, 3])

    def test_get_tag_ids_no_existing_no_new_tags(self):
        # Given: Document has no tags, and no new tags found in metadata
        self.mock_tag_service.get_tag_names_by_ids.return_value = []
        self.mock_tag_service.get_tag_ids_by_names.return_value = []

        # When: get_tag_ids is called
        tag_ids = self.paperless_service.get_tag_ids([], [])

        # Then: No tags should be created or returned
        self.assertEqual(tag_ids, [])

    def test_post_process_correct_tags(self):
        # Given: Tag service returns correct tag IDs
        self.mock_tag_service.get_tag_ids_by_names.return_value = [10, 11]
        self.mock_tag_service.create_tags.return_value = []

        # When: post_process is called
        post_processed_document = self.paperless_service.post_process(self.document, self.metadata)

        # Then: Tags should be set correctly
        self.assertEqual(post_processed_document.tags, [10, 11])

    def test_post_process_title_from_metadata(self):
        # Given: Metadata has an updated title
        # When: post_process is called
        post_processed_document = self.paperless_service.post_process(self.document, self.metadata)

        # Then: The title should be updated from metadata
        self.assertEqual(post_processed_document.title, "Updated Title")

    def test_post_process_created_date_from_metadata(self):
        # Given: Metadata has an updated created date
        # When: post_process is called
        post_processed_document = self.paperless_service.post_process(self.document, self.metadata)

        # Then: The created date should be updated from metadata
        self.assertEqual(post_processed_document.created, "2024-02-01")


if __name__ == '__main__':
    unittest.main()
