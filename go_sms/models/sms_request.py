import requests
import json


class SMSApi:

    def __init__(self, config):
        self.config = config
        self.headers = {}

    def make_api_request(self, service_endpoint="SendSMS", params=None):
        base_url = self.config.smpp_server.rstrip("/")
        service_url = f"{base_url}/{service_endpoint}"
        try:
            res = requests.get(
                service_url, headers=self.headers, params=params, timeout=15
            )
            res.raise_for_status()
            try:
                return json.loads(res.text)
            except ValueError:
                return {"status": "1710", "message": "Internal error"}

        except requests.RequestException as e:
            return {"status": "1710", "message": "Internal error"}
