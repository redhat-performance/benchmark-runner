
import requests
import json
import logging

logging.basicConfig(level=logging.INFO)


class GrafanaOperations:
    """
    This class is responsible for Grafana operations
    """
    def __init__(self, grafana_url: str, grafana_api_key: str, grafana_json_path: str, grafana_folder_name: str):
        self.grafana_url = grafana_url
        self.grafana_api_key = grafana_api_key
        self.grafana_json_path = grafana_json_path
        self.dashboard_data = {}
        self.logger = logging.getLogger(__name__)
        self.__grafana_folder_name = grafana_folder_name

    def fetch_all_dashboards(self):
        """
        This method fetches all dashboards
        :return:
        """
        dashboard_list = []
        headers = {
            "Authorization": f"Bearer {self.grafana_api_key}",
        }

        try:
            response = requests.get(f"{self.grafana_url}/api/search", headers=headers)

            if response.status_code == 200:
                dashboards = response.json()
                for dashboard in dashboards:
                    dashboard_list.append(f"Dashboard ID: {dashboard['id']}, Title: {dashboard['title']}")
            else:
                raise Exception(f"Failed to fetch dashboards. Status code: {response.status_code}. Message: {response.text}")
            return dashboard_list
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching dashboards: {e}")

    def increment_dashboard_version(self):
        """
        This method increments dashboard version
        :return:
        """
        self.dashboard_data["version"] = self.get_latest_dashboard_version()

    def read_dashboard_json(self):
        """
        This method reads dashboard from json into dictionary
        :return:
        """
        with open(self.grafana_json_path, 'r') as f:
            self.dashboard_data = json.load(f)

    def write_dashboard_json(self):
        """
        This method writes dashboard data into json
        :return:
        """
        with open(self.grafana_json_path, 'w') as json_file:
            json.dump(self.dashboard_data, json_file, indent=2)

    def get_latest_dashboard_version(self):
        """
        This method get latest dashboard version
        :return:
        """
        headers = {
            "Authorization": f"Bearer {self.grafana_api_key}",
        }
        try:
            response = requests.get(f"{self.grafana_url}/api/dashboards/uid/{self.dashboard_data['uid']}", headers=headers)
            response_json = response.json()
            return response_json['dashboard']['version']

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching dashboard version: {e}")

    def get_dashboard_folder_id(self):
        """
        This method gets dashboard folder id according to grafana folder name
        """
        headers = {
            "Authorization": f"Bearer {self.grafana_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(
                f"{self.grafana_url}/api/search",
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                for item in data:
                    if item.get('type') == 'dash-folder' and item.get('title') == self.__grafana_folder_name:
                        return item['id']

            raise Exception(f"Folder with name '{self.__grafana_folder_name}' not found.")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error retrieving folder ID: {e}")

    def override_dashboard(self):
        """
        This method overrides dashboard with new json
        :return:
        """
        headers = {
            "Authorization": f"Bearer {self.grafana_api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=headers,
                json={
                    "dashboard": self.dashboard_data,
                    "folderId": self.get_dashboard_folder_id()  # Specify the folder ID here
                },
            )

            if response.status_code == 200:
                self.logger.info(f"Dashboard '{self.dashboard_data['title']}' overridden successfully.")
            else:
                # The 412 status code is used when a newer dashboard already exists.
                raise Exception(
                    f"Failed to override dashboard '{self.dashboard_data['title']}'. Status code: {response.status_code}. Message: {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Error overriding dashboard '{self.dashboard_data['title']}': {e}")
