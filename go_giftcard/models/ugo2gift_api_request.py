import json
import logging

import requests

_logger = logging.getLogger(__name__)


class Ugo2GiftAPI:

    def __init__(self, env, api_url, api_key, api_secret, headers=None):
        self.env = env
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = api_url.rstrip("/")
        self.headers = headers or {"Content-Type": "application/json"}

    def get_token(self, endpoint):
        token_url = f"{self.base_url}{endpoint}"
        payload = {"apiKey": self.api_key, "apiSecret": self.api_secret}

        response = self._post_request(token_url, payload, auth=None)
        if not response.get("success"):
            return None

        data = response.get("data", {})
        token = None
        if isinstance(data, dict):
            token = data.get("data", {}).get("accessToken", {}).get("token")

        if not token:
            return None

        return token

    def post_message(self, message):
        """Send notification to user and log warning."""
        self.env["bus.bus"]._sendone(
            self.env.user.partner_id,
            "simple_notification",
            {
                "title": "Information",
                "message": message,
                "sticky": False,
                "warning": True,
            },
        )

    def get_brand(self, endpoint="brands"):
        country_id = int(
            self.env["ir.config_parameter"].sudo().get_param("go_giftcard.brand_country_id", 0)
        )
        country_code = "QA"
        if country_id:
            country = self.env["res.country"].browse(country_id)
            if country.exists() and country.code:
                country_code = country.code

        final_url = f"{self.base_url}/{endpoint}/?country={country_code}"
        # final_url = "https://private-anon-12659dab9a-ygagcorporaterewards.apiary-mock.com/corporate/api/v2-4/brands/"
        return self._request(final_url, method="GET")

    def create_gift_order(self, payload, auth):
        final_url = f"{self.base_url}/v2-4/orders/"
        return self._request(final_url, method="POST", payload=payload, auth=auth)

    def post_cardmoola_order(self, payload):
        url = f"{self.base_url}/order/save"
        return self._request(url, method="POST", payload=payload)

    def create_skipcash_payment(
        self, payload, endpoint="/v1/payments", headers=None
    ):
        base_url = self.base_url.rstrip("/")
        endpoint = endpoint.lstrip("/")
        final_url = f"{base_url}/{endpoint}"

        return self._request(final_url, method="POST", payload=payload, use_json=False)

    def _request(
        self, url, method="GET", params=None, payload=None, auth=None, use_json=True
    ):
        method = method.upper()
        if method == "GET":
            return self._get_request(url, params=params)
        elif method == "POST":
            return self._post_request(url, payload, auth=auth, use_json=use_json)
        else:
            return {
                "status": 0,
                "success": False,
                "data": None,
                "error": f"Unsupported HTTP method: {method}",
            }

    def _get_request(self, url, params=None):
        all_data = []
        try:
            page = 1
            query_params = dict(params or {}, page=page)

            while True:
                resp = requests.get(url, headers=self.headers, params=query_params)
                success = resp.status_code in (200, 201)

                try:
                    data = resp.json()
                except Exception as e:
                    _logger.warning("ugo2gift: JSON parse error: %s", e)
                    data = {}

                if not success:
                    return {
                        "status": resp.status_code,
                        "success": False,
                        "data": None,
                        "error": data or resp.text,
                    }

                # Collect brand data if available
                if isinstance(data, dict) and "brands" in data:
                    current_page = data.get("current_page")
                    next_page = data.get("next")

                    if page == current_page:
                        all_data.extend(data.get("brands", []))
                    else:
                        break

                    if not next_page:
                        break

                    page += 1
                    query_params = dict(params or {}, page=page)
                else:
                    break

            return {
                "status": 200,
                "success": True,
                "data": all_data,
                "error": None,
            }

        except requests.RequestException as e:
            return {"status": 0, "success": False, "data": None, "error": str(e)}

    def _post_request(self, url, payload, auth=None, use_json=True):
        try:
            if use_json:
                res = requests.post(url, json=payload, headers=self.headers, auth=auth)
            else:
                res = requests.post(
                    url, data=json.dumps(payload), headers=self.headers, timeout=30
                )

            success = res.status_code in (200, 201)
            data = None
            try:
                data = res.json()
            except ValueError as e:
                _logger.info(
                    "Got Value Error While sending request to ugo2gift", str(e)
                )

            return {
                "status": res.status_code,
                "success": success,
                "data": data if success else None,
                "error": None if success else data or res.text,
            }

        except requests.RequestException as e:
            _logger.info("error", str(e))
            return {"status": 0, "success": False, "data": None, "error": str(e)}
