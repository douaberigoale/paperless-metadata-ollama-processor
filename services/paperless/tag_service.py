import requests


class TagService:
    def __init__(self, logger, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token
        self.logger = logger

    def get_all(self):
        url = f"{self.api_url}/tags/"
        headers = {
            "Authorization": f"Token {self.api_token}"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            self.logger.log_error(f"Error fetching tags: {e}")
            raise

    def get_all_names(self):
        return [tag['name'] for tag in self.get_all()]

    def get_tag_names_by_ids(self, tag_ids):
        all_tags = self.get_all()
        tag_map = {tag['id']: tag['name'] for tag in all_tags}

        tag_names = [tag_map.get(tag_id) for tag_id in tag_ids if tag_map.get(tag_id) is not None]
        return tag_names

    def get_tag_ids_by_names(self, tag_names):
        """
        Retrieve tag IDs based on tag names.
        """
        all_tags = self.get_all()
        tag_map = {tag['name'].lower(): tag['id'] for tag in all_tags}

        tag_ids = [tag_map.get(tag_name.lower()) for tag_name in tag_names if tag_map.get(tag_name.lower()) is not None]
        return tag_ids

    def create_tags(self, new_tags):
        url = f"{self.api_url}/tags/"
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        created_tag_ids = []

        for tag in new_tags:
            data = {
                "name": tag,
                "matching_algorithm": 6  # set by default to automatic matching
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                created_tag_ids.append(response.json()['id'])
            except requests.exceptions.RequestException as e:
                self.logger.log_error(f"Error creating tag '{tag}': {e}")
                raise

        return created_tag_ids
