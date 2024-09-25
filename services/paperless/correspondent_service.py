import requests


class CorrespondentService:
    def __init__(self, logger, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token
        self.logger = logger

    def get_all(self):
        url = f"{self.api_url}/correspondents/"
        headers = {
            "Authorization": f"Token {self.api_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error fetching correspondents: {e}")
            raise

    def get_all_names(self):
        return [correspondent['name'] for correspondent in self.get_all()]

    def get_correspondent_name_by_id(self, correspondent_id):
        all_correspondents = self.get_all()
        correspondent_map = {correspondent['id']: correspondent['name'] for correspondent in all_correspondents}
        return correspondent_map.get(correspondent_id)

    def get_correspondent_id_by_name(self, name):
        all_correspondents = self.get_all()
        correspondent_map = {correspondent['name'].lower(): correspondent['id'] for correspondent in all_correspondents}

        return correspondent_map.get(name.lower())

    def create_correspondent(self, name):
        url = f"{self.api_url}/correspondents/"
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
            self.logger.log_error(f"Error creating correspondent '{name}': {e}")
            raise
