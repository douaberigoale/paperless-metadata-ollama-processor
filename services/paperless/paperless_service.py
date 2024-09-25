from logger import Logger
from models.document import Document
from models.extracted_metadata import ExtractedMetadata
from models.postprocessed_document import PostProcessedDocument
from services.paperless.correspondent_service import CorrespondentService
from services.paperless.document_type_service import DocumentTypeService
from services.paperless.tag_service import TagService


class PaperlessService:
    def __init__(self, logger: Logger,
                 tag_service: TagService,
                 correspondent_service: CorrespondentService,
                 document_type_service: DocumentTypeService):
        self.logger = logger
        self.tag_service = tag_service
        self.correspondent_service = correspondent_service
        self.document_type_service = document_type_service

    def post_process(self, document: Document, metadata: ExtractedMetadata):
        title = metadata.title or document.title
        date = metadata.created_date or document.created_date
        tag_ids = self.get_tag_ids(document.tag_ids, metadata.tags)
        correspondent_id = document.correspondent_id or self.get_correspondent_id(metadata.correspondent)
        document_type_id = document.document_type_id or self.get_document_type_id(metadata.document_type)

        post_processed_document = PostProcessedDocument(
            title=title,
            created=date,
            correspondent=correspondent_id,
            document_type=document_type_id,
            tags=tag_ids
        )

        return post_processed_document

    def get_tag_ids(self, document_tag_ids, processed_tags):
        existing_tags = set(self.tag_service.get_tag_names_by_ids(document_tag_ids))
        combined_tags = set(existing_tags.union([tag.lower() for tag in processed_tags]))

        existing_tag_ids = self.tag_service.get_tag_ids_by_names(combined_tags)
        new_tags = combined_tags - set(self.tag_service.get_tag_names_by_ids(existing_tag_ids))

        if not new_tags:
            return existing_tag_ids

        new_tag_ids = self.tag_service.create_tags(new_tags)
        return existing_tag_ids + new_tag_ids

    def get_correspondent_id(self, correspondent):
        if correspondent:
            correspondent_id = self.correspondent_service.get_correspondent_id_by_name(correspondent)

            if correspondent_id:
                return correspondent_id

            correspondent_id = self.correspondent_service.create_correspondent(correspondent)
            return correspondent_id

        return None

    def get_document_type_id(self, document_type):
        if document_type:
            document_type_id = self.document_type_service.get_document_type_id_by_name(document_type)

            if document_type_id:
                return document_type_id

            document_type_id = self.document_type_service.create_document_type(document_type)
            return document_type_id

        return None
