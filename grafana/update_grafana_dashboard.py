
import os
import requests
import json

# Access environment variables using os.environ
grafana_url = os.environ.get('PERF_GRAFANA_URL', '')
api_key = os.environ.get('PERF_GRAFANA_API_KEY', '')
json_dashboard_path = os.environ.get('PERF_GRAFANA_JSON', 'perf/output.json')


class GrafanaOperations:
    """
    This class responsible for Grafana operations
    """
    def __init__(self, grafana_url, api_key, json_dashboard_path):
        self.grafana_url = grafana_url
        self.api_key = api_key
        self.json_dashboard_path = json_dashboard_path
        self.dashboard_data = {}

    def fetch_all_dashboards(self):
        """
        This method fetches all dashboards
        :return:
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = requests.get(f"{self.grafana_url}/api/search", headers=headers)

            if response.status_code == 200:
                dashboards = response.json()
                for dashboard in dashboards:
                    print(f"Dashboard ID: {dashboard['id']}, Title: {dashboard['title']}")
            else:
                print(f"Failed to fetch dashboards. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching dashboards: {e}")

    def increment_dashboard_version(self):
        """
        This method increases dashboard version
        :return:
        """
        self.dashboard_data["version"] = self.get_latest_dashboard_version()

    def read_dashboard_json(self):
        """
        This method reads dashboard from json into dictionary
        :return:
        """
        with open(self.json_dashboard_path, 'r') as f:
            self.dashboard_data = json.load(f)

    def write_dashboard_json(self):
        """
        This method writes dashboard data into json
        :return:
        """
        with open(self.json_dashboard_path, 'w') as json_file:
            json.dump(self.dashboard_data, json_file, indent=2)

    def get_latest_dashboard_version(self):
        """
        This method get latest dashboard version
        :return:
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        try:
            response = requests.get(f"{self.grafana_url}/api/dashboards/uid/{self.dashboard_data['uid']}", headers=headers)
            response_json = response.json()
            return response_json['dashboard']['version']

        except requests.exceptions.RequestException as e:
            print(f"Error fetching dashboard version: {e}")
            return None

    def override_dashboard(self):
        """
        This method overrides dashboard with new json
        :return:
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(
                f"{self.grafana_url}/api/dashboards/db",
                headers=headers,
                json={"dashboard": self.dashboard_data},
            )

            if response.status_code == 200:
                print(f"Dashboard '{self.dashboard_data['title']}' overridden successfully.")
            else:
                print(
                    f"Failed to override dashboard '{self.dashboard_data['title']}'. Status code: {response.status_code}. Message: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Error overriding dashboard '{self.dashboard_data['title']}': {e}")


grafana_operations = GrafanaOperations(grafana_url=grafana_url,
                                       api_key=api_key,
                                       json_dashboard_path=json_dashboard_path)

# Update generate grafana dashboard
# for debug: grafana_operations.fetch_all_dashboards()
grafana_operations.read_dashboard_json()
grafana_operations.increment_dashboard_version()
grafana_operations.override_dashboard()

# Error: 412 - need to find last working index
# The 412 status code is used when a newer dashboard already exists (newer, its version is greater than the version that was sent). The same status code is also used if another dashboard exists with the same title.