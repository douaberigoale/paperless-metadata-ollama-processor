import sys
import requests
from logger import Logger
from models.document import Document


class DocumentReader:
    def __init__(self, logger: Logger):
        self.logger = logger

    def get_document(self, doc_id, url, headers):
        response = None

        try:
            response = _fetch_document_response(doc_id, url, headers)
            _check_for_empty_response(doc_id, response)
            _check_for_non_json_response(doc_id, response)
            return _parse_document(response)

        except Exception as e:
            self.log_exception(e, response)
            raise

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


def _fetch_document_response(doc_id, paperless_documents_url, headers):
    response = requests.get(f"{paperless_documents_url}{doc_id}/", headers=headers)
    response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
    return response


def _parse_document(response):
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


def _check_for_empty_response(doc_id, response):
    if not response.text:
        raise ValueError(f"Empty response for document ID {doc_id}")


def _check_for_non_json_response(doc_id, response):
    if 'application/json' not in response.headers.get('Content-Type', ''):
        raise ValueError(f"Non-JSON response for document ID {doc_id}: {response.text}")
