import logging
import os

import requests


class SlackOperations:
    """Slack messaging operations for PerfCI notifications."""

    SLACK_POST_API = 'https://slack.com/api/chat.postMessage'

    def __init__(self):
        self.__slack_auth_token = os.environ['SLACK_API_TOKEN']
        self.__channel_name = os.environ['SLACK_CHANNEL_NAME']
        self.api_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.__slack_auth_token}'
        }

    def post_message(self, text: str):
        json_data = {
            'channel': self.__channel_name,
            'text': text
        }
        response = requests.post(url=self.SLACK_POST_API, headers=self.api_headers, json=json_data, timeout=30)
        response_data = response.json()
        if not response_data.get('ok'):
            logging.error("Slack post failed: %s", response_data.get('error'))
        return response_data
