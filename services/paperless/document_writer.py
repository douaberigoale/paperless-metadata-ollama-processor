from dataclasses import asdict
import requests
from logger import Logger
from models.postprocessed_document import PostProcessedDocument


class DocumentWriter:
    def __init__(self, logger: Logger):
        self.logger = logger

    def update_document(self, doc_id, post_processed_document: PostProcessedDocument, paperless_documents_url, headers):
        try:
            data = asdict(post_processed_document)
            self.logger.log(f"Updating Paperless document with metadata: {data}")
            update_response = requests.patch(f"{paperless_documents_url}{doc_id}/",
                                             json=data,
                                             headers=headers)
            update_response.raise_for_status()
            return update_response.status_code
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error updating Paperless document ID {doc_id}: {e}")
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error updating document ID {doc_id}: {e}")
            raise
