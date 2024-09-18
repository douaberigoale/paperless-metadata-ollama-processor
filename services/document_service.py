import sys
from dataclasses import asdict

import requests
from logger import Logger
from models.document import Document
from models.postprocessed_document import PostProcessedDocument


class DocumentService:
    def __init__(self, logger: Logger, api_url, token):
        self.logger = logger
        self.paperless_documents_url = f'{api_url}/documents/'
        self.headers = {'Authorization': f'Token {token}'}

    def get_document(self, doc_id):
        try:
            response = requests.get(f"{self.paperless_documents_url}{doc_id}/", headers=self.headers)
            response.raise_for_status()
            document_data = response.json()

            document = Document(
                id=document_data['id'],
                title=document_data['title'],
                created_date=document_data['created_date'],
                text=document_data['content'],
                correspondent_id=document_data.get('correspondent'),
                document_type_id=document_data.get('document_type'),
                tag_ids=document_data.get('tags', [])
            )

            return document
        except requests.exceptions.HTTPError as e:
            self.logger.log_error(f"HTTP error: {e}", sys.argv)
            raise

    def update_document(self, doc_id, post_processed_document: PostProcessedDocument):
        try:
            data = asdict(post_processed_document)
            self.logger.log(f"Updating Paperless document with metadata: {data}")
            update_response = requests.patch(f"{self.paperless_documents_url}{doc_id}/",
                                             json=data,
                                             headers=self.headers)

            return update_response.status_code
        except Exception as e:
            self.logger.log_error(f"Error updating Paperless document ID {doc_id}: {e}")
            raise
