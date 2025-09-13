from odoo import http, _
from odoo.http import request
import uuid
import json
import logging

_logger = logging.getLogger(__name__)


class GiftCardController(http.Controller):

    def _get_json_request(self):
        try:
            if not request.httprequest.data:
                return {"error": _("No JSON payload provided")}

            data = json.loads(request.httprequest.data.decode("utf-8"))
            if not isinstance(data, dict):
                return {"error": _("Invalid JSON format")}
            return data
        except json.JSONDecodeError:
            return {"error": _("Malformed JSON payload")}

    def _validate_token(self, data):
        token = data.get("token")
        if not token:
            return {"error": _("Token is missing")}
        user = request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
        if not user:
            return {"error": _("Invalid User Token")}
        return user

    def _check_required_fields(self, data, required_fields):
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            return {
                "error": _("Missing required field(s): %s" % ", ".join(missing_fields))
            }
        return None

    def _prepare_gift_vals(self, data, is_from_cardmoola=False):
        qar_currency = (
            request.env["res.currency"].search([("name", "=", "QAR")], limit=1).id
        )

        country = (
            request.env["res.country"]
            .search([("code", "=", data.get("country"))], limit=1)
            .id
            if data.get("country")
            else False
        )

        currency_org = (
            request.env["res.currency"]
            .search([("name", "=", data.get("currency_org"))], limit=1)
            .id
            if data.get("currency_org")
            else False
        )

        delivery_language = (
            request.env["res.lang"]
            .search([("iso_code", "=", data.get("delivery_language"))], limit=1)
            .id
            if data.get("delivery_language")
            else False
        )

        base_vals = {
            "reference_id": data.get("reference_id", str(uuid.uuid4())),
            "currency_id": qar_currency,
            "amount": data.get("amount"),
            "message": data.get("message", ""),
            "customer_id": data.get("customer_id"),
            "return_url": data.get("return_url"),
            "currency_org_id": currency_org,
            "amount_org": data.get("amount_org"),
        }

        if is_from_cardmoola:
            base_vals.update(
                {
                    "brand_code": "CARDMOOLA",
                    "is_cardmoola": True,
                    "cardmoola_product_id": data.get("product_id"),
                    "receiver_name": data.get("customer_name"),
                    "receiver_email": data.get("customer_email"),
                    "receiver_phone": data.get("customer_phone"),
                }
            )
        else:
            base_vals.update(
                {
                    "brand_code": data.get("brand_code"),
                    "notify": data.get("notify", False),
                    "country_id": country,
                    "delivery_language_id": delivery_language,
                    "receiver_name": data.get("receiver_name"),
                    "receiver_email": data.get("receiver_email"),
                    "receiver_phone": data.get("receiver_phone"),
                }
            )

        return base_vals

    def _create_gift_card(self, vals):
        return request.env["gift.card"].sudo().create(vals)

    def _generate_payment_url(self, gift):
        payment_data = gift.get_skipcash_url()
        if not payment_data:
            return {"error": _("Failed to generate payment link")}
        gift.payment_web_link = payment_data.get("pay_url")
        gift.payment_id = payment_data.get("id")
        return gift

    @http.route(
        ["/go/api/user/ugo2gift/create"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def create_gift_card(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        required_fields = [
            "amount",
            "reference_id",
            "brand_code",
            "country",
            "customer_id",
            "currency",
        ]
        error = self._check_required_fields(data, required_fields)
        if error:
            return error

        vals = self._prepare_gift_vals(data)

        try:
            gift = self._create_gift_card(vals)
        except Exception as e:
            return {"error": _("Failed to create gift card")}

        try:
            gift = self._generate_payment_url(gift)
        except Exception as e:
            return {"error": _("Failed to generate payment url")}

        return {
            "id": gift.id,
            "name": gift.name,
            "reference_id": gift.reference_id,
            "payment_web_link": gift.payment_web_link,
            "state": gift.state,
        }

    @http.route(
        ["/cardmola/payment/request"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def create_get_sales_cardmoola(self, **post):

        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        required_fields = [
            "product_id",
            "customer_id",
            "customer_name",
            "customer_phone",
            "customer_email",
            "amount",
            "return_url",
        ]
        error = self._check_required_fields(data, required_fields)
        if error:
            return error

        vals = self._prepare_gift_vals(data, is_from_cardmoola=True)

        try:
            gift = self._create_gift_card(vals)
        except Exception as e:
            return {"error": _("Failed to create gift card")}

        try:
            gift = self._generate_payment_url(gift)
            if isinstance(gift, dict) and "error" in gift:
                return gift
        except Exception as e:
            _logger.exception("Payment URL generation failed")
            return {"error": _("Failed to generate payment URL")}

        return {
            "id": gift.id,
            "name": gift.name,
            "reference_id": gift.reference_id,
            "payment_web_link": gift.payment_web_link,
            "state": gift.state,
        }

    def _prepare_gift_response(self, gift):
        pg_state = "Paid" if gift.state == "paid" else "Not Paid"
        brand_logo = (
            request.env["ugo2gift.brand"]
            .sudo()
            .search(
                [
                    ("brand_code", "=", gift.brand_code),
                    ("logo_url", "!=", False),
                ],
                limit=1,
            )
        )
        return {
            "reference_id": gift.reference_id,
            "brand_code": gift.brand_code,
            "barnd_logo": brand_logo.logo_url,
            "notify": gift.notify,
            "currency": gift.currency_id.name,
            "amount": gift.amount,
            "country": gift.country_id.name,
            "receiver_name": gift.receiver_name,
            "receiver_email": gift.receiver_email,
            "receiver_phone": gift.receiver_phone,
            "message": gift.message,
            "customer_id": gift.customer_id.id,
            "expiry_date": gift.expiry_date,
            "redemption_instructions": gift.redemption_instructions,
            "barcode": gift.barcode,
            "egift_card_url": gift.egift_card_url,
            "gift_verification_pin": gift.gift_verification_pin,
            "delivery_language": gift.delivery_language_id.iso_code,
            "order_id": gift.order_id,
            "status": gift.state,
            "payment_status": pg_state,
        }

    @http.route(
        ["/go/api/user/ugo2gift/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def unpaid_sales_transaction_list(self, **post):

        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict) and "error" in current_user:
            return current_user

        customer_id = data.get("customer_id")
        if not customer_id:
            return {"error": _("Customer ID is missing")}

        gifts = (
            request.env["gift.card"].sudo().search([("customer_id", "=", customer_id)])
        )
        if not gifts:
            return {"error": _("No Gift Cards found for this Customer")}

        return [self._prepare_gift_response(gift) for gift in gifts]

    @http.route(
        ["/go/api/user/ugo2gift/bought/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def paid_sales_transaction_list(self, **post):

        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict) and "error" in current_user:
            return current_user

        customer_id = data.get("customer_id")
        if not customer_id:
            return {"error": _("Customer ID is missing")}

        gifts = (
            request.env["gift.card"]
            .sudo()
            .search([("customer_id", "=", customer_id), ("state", "=", "paid")])
        )
        if not gifts:
            return {"error": _("No Gift Cards found for this Customer")}

        return [self._prepare_gift_response(gift) for gift in gifts]

    @http.route(
        ["/go/api/user/ugo2gift/search/id"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def search_giftcard_by_reference(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict) and "error" in current_user:
            return current_user

        reference_id = data.get("reference_id")
        if not reference_id:
            return {"error": _("Reference ID is missing")}

        gifts = (
            request.env["gift.card"]
            .sudo()
            .search([("reference_id", "=", reference_id)])
        )
        if not gifts:
            return {"error": _("No Gift Cards found for this Reference ID")}

        return [self._prepare_gift_response(gift) for gift in gifts]

    @http.route(
        [
            "/go/api/user/cardmoola/search/id",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def search_cardmoola_by_reference(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict) and "error" in current_user:
            return current_user

        reference_id = data.get("reference_id")
        if not reference_id:
            return {"error": _("Reference ID is missing")}

        gifts = (
            request.env["gift.card"]
            .sudo()
            .search([("reference_id", "=", reference_id), ("is_cardmoola", "=", True)])
        )
        if not gifts:
            return {"error": _("No Gift Cards found for this Reference ID")}

        datas = []
        for gift in gifts:
            response = self._prepare_gift_response(gift)
            for field in ["notify", "country", "egift_card_url", "brand_code"]:
                response.pop(field, None)
            response.update(
                {
                    "barnd_logo": "",
                    "giftcard_company": gift.brand_code,
                }
            )
            datas.append(response)

        return datas
