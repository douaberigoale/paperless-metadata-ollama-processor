import requests


class DocumentTypeService:
    def __init__(self, logger, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token
        self.logger = logger

    def get_all(self):
        url = f"{self.api_url}/document_types/"
        headers = {
            "Authorization": f"Token {self.api_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error fetching document types: {e}")
            raise

    def get_all_names(self):
        return [doc_type['name'] for doc_type in self.get_all()]

    def get_document_type_name_by_id(self, document_type_id):
        all_document_types = self.get_all()
        document_type_map = {doc_type['id']: doc_type['name'] for doc_type in all_document_types}
        return document_type_map.get(document_type_id)

    def get_document_type_id_by_name(self, name):
        all_document_types = self.get_all()
        document_type_map = {doc_type['name'].lower(): doc_type['id'] for doc_type in all_document_types}

        return document_type_map.get(name.lower())

    def create_document_type(self, name):
        url = f"{self.api_url}/document_types/"
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }

        data = {
            "name": name,
            "matching_algorithm": 6  # set by default to automatic matching
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()['id']
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error creating document type '{name}': {e}")
            raise
