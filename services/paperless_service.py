import sys
import requests
from logger import Logger


class PaperlessService:
    def __init__(self, logger: Logger, api_url, token):
        self.paperless_api_url = api_url
        self.paperless_documents_url = f'{self.paperless_api_url}/documents/'
        self.paperless_tags_url = f'{self.paperless_api_url}/tags/'
        self.paperless_types_url = f'{self.paperless_api_url}/document_types/'
        self.paperless_correspondents_url = f'{self.paperless_api_url}/correspondents/'
        self.paperless_api_token = token

        self.headers = {'Authorization': f'Token {self.paperless_api_token}'}
        self.logger = logger

    def get_document_text(self, doc_id):
        try:
            self.logger.log(f"Extracting text for document ID: {doc_id}")
            response = requests.get(f"{self.paperless_documents_url}{doc_id}/", headers=self.headers)
            response.raise_for_status()
            document = response.json()
            return document.get('content', None)
        except requests.exceptions.HTTPError as e:
            self.logger.log_error(f"HTTP error: {e}", sys.argv)
            raise
        except Exception as e:
            self.logger.log_error(f"Error extracting OCR text: {e}", sys.argv)
            raise

    def get_existing_metadata(self):
        try:
            tags_response = requests.get(self.paperless_tags_url, headers=self.headers)
            types_response = requests.get(self.paperless_types_url, headers=self.headers)
            correspondents_response = requests.get(self.paperless_correspondents_url, headers=self.headers)

            tags = [tag['name'] for tag in tags_response.json()['results']]
            document_types = [doc_type['name'] for doc_type in types_response.json()['results']]
            correspondents = [corr['name'] for corr in correspondents_response.json()['results']]
            return tags, document_types, correspondents
        except Exception as e:
            self.logger.log_error(f"Error retrieving existing data: {e}")
            raise

    def update_document(self, doc_id, new_metadata):
        try:
            self.logger.log(f"Fetching existing metadata for document ID: {doc_id}")
            response = requests.get(f"{self.paperless_documents_url}{doc_id}/", headers=self.headers)
            response.raise_for_status()
            document = response.json()

            # Update title
            document['title'] = new_metadata.get('title', document['title'])

            # Append tags, avoid duplicates
            existing_tags = {tag['name'] for tag in document.get('tags', [])}
            new_tags = set(new_metadata.get('tags', []))
            combined_tags = list(existing_tags.union(new_tags))
            document['tags'] = combined_tags

            # Set correspondent only if empty
            if not document.get('correspondent'):
                document['correspondent'] = new_metadata.get('correspondent')

            # Set document type only if empty
            if not document.get('type'):
                document['type'] = new_metadata.get('type')

            # Log and update document
            self.logger.log(f"Updating Paperless document ID {doc_id} with new metadata: {document}")
            update_response = requests.patch(f"{self.paperless_documents_url}{doc_id}/", json=document, headers=self.headers)
            update_response.raise_for_status()

            return update_response.status_code
        except Exception as e:
            self.logger.log_error(f"Error updating Paperless document ID {doc_id}: {e}")
            raise
