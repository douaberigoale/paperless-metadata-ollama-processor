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
        response = None

        try:
            response = self.fetch_document_response(doc_id)
            self.check_for_empty_response(doc_id, response)
            self.check_for_non_json_response(doc_id, response)
            return self.parse_document(response)

        except Exception as e:
            self.log_exception(e, response)
            raise

    def fetch_document_response(self, doc_id):
        response = requests.get(f"{self.paperless_documents_url}{doc_id}/", headers=self.headers)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
        return response

    def parse_document(self, response):
        document_data = response.json()
        return Document(
            id=document_data['id'],
            title=document_data['title'],
            created_date=document_data['created_date'],
            text=document_data['content'],
            correspondent_id=document_data.get('correspondent'),
            document_type_id=document_data.get('document_type'),
            tag_ids=document_data.get('tags', [])
        )

    def check_for_empty_response(self, doc_id, response):
        if not response.text:
            raise ValueError(f"Empty response for document ID {doc_id}")

    def check_for_non_json_response(self, doc_id, response):
        if 'application/json' not in response.headers.get('Content-Type', ''):
            raise ValueError(f"Non-JSON response for document ID {doc_id}: {response.text}")

    def log_exception(self, exception, response):
        if isinstance(exception, requests.exceptions.JSONDecodeError):
            self.logger.log_error(
                f"JSON decode error: {exception}, Response: {getattr(response, 'text', 'No response')}", sys.argv)
        elif isinstance(exception, requests.exceptions.RequestException):
            self.logger.log_error(
                f"Request exception: {exception}, Response: {getattr(response, 'text', 'No response')}", sys.argv)
        elif isinstance(exception, ValueError):
            self.logger.log_error(f"Value error: {exception}", sys.argv)
        else:
            self.logger.log_error(
                f"Unexpected error: {exception}, Response: {getattr(response, 'text', 'No response')}", sys.argv)

    def update_document(self, doc_id, post_processed_document: PostProcessedDocument):
        try:
            data = asdict(post_processed_document)
            self.logger.log(f"Updating Paperless document with metadata: {data}")
            update_response = requests.patch(f"{self.paperless_documents_url}{doc_id}/",
                                             json=data,
                                             headers=self.headers)
            update_response.raise_for_status()  # Ensure we catch HTTP errors for updates
            return update_response.status_code
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error updating Paperless document ID {doc_id}: {e}")
            raise
        except Exception as e:
            self.logger.log_error(f"Unexpected error updating document ID {doc_id}: {e}")
            raise
