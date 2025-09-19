from odoo import http, _
from odoo.http import request
import json
from datetime import datetime, timedelta
import requests


class Voucher(http.Controller):

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

    def _format_voucher_data(self, voucher):
        return {
            "id": voucher.id,
            "logo": voucher.logo,
            "code": voucher.code,
            "expiry_date": voucher.expiry_date,
            "status": voucher.state,
            "name": voucher.name,
            "name_arabic": voucher.name_arabic,
            "voucher_amount": voucher.voucher_amount,
            "discount_value": voucher.discount_value,
            "discount_type": voucher.discount_type,
            "terms_condition": voucher.terms_condition,
            "terms_condition_ar": voucher.terms_condition_arabic,
            "delivery_charge": voucher.delivery_charge,
            "cash": voucher.cash,
            "x_bank_charge": voucher.bank_charge,
            "x_phone": voucher.phone,
            "x_merchant_logo": voucher.merchant_logo,
        }

    @http.route(
        [
            '/go/api/user/voucher/list',
        ],
        auth="public",
        website=True,
        methods=['POST'],
        csrf=False,
        type='json',
        cors='*'
    )
    def get_voucher_list(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        discount_vouchers = request.env['discount.voucher'].sudo().search([])

        result = []
        for voucher in discount_vouchers:
            result.append(self._format_voucher_data(voucher))

        return result

    @http.route(
        ["/go/api/user/voucher/details"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_voucher_details(self, **post):
        data = post or self._get_json_request()

        if "error" in data:
            return data

        code = data.get("code")
        if not code:
            return {"error": _("Voucher code is required")}

        discount_voucher = (
            request.env["discount.voucher"]
            .sudo()
            .search([("code", "=", code)], limit=1)
        )

        if not discount_voucher:
            return {"error": _("This Voucher Code is not available")}

        return {
            "code": discount_voucher.code,
            "name": discount_voucher.name,
            "name_arabic": discount_voucher.name_arabic,
            "discount_value": discount_voucher.discount_value,
            "discount_type": discount_voucher.discount_type,
            "expiry_date": discount_voucher.expiry_date,
            "terms_condition": discount_voucher.terms_condition,
            "state": discount_voucher.state,
            "logo": discount_voucher.logo,
        }

    def _get_valid_voucher(self, code):

        if not code:
            return {"error": _("Voucher code is required")}

        voucher = (
            request.env["discount.voucher"]
            .sudo()
            .search([("code", "=", code)], limit=1)
        )
        if not voucher:
            return {"error": _("This Voucher Code is not available")}

        if voucher.state == "expired":
            return {"error": _("Voucher is expired")}

        if voucher.state == "draft":
            return {"error": _("Voucher is not activated")}

        return voucher

    @http.route(
        ["/go/api/user/voucher/apply"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def action_apply_voucher(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        voucher = self._get_valid_voucher(data.get("code"))
        if isinstance(voucher, dict) and "error" in voucher:
            return voucher

        redeemed_user = (
            request.env["voucher.redeemed.user"]
            .sudo()
            .search(
                [
                    ("discount_voucher_id", "=", voucher.id),
                    ("user_id", "=", user.id),
                ],
                limit=1,
            )
        )
        if redeemed_user:
            return {"error": _("You have already redeemed this voucher")}

        request.env["voucher.redeemed.user"].sudo().create(
            {
                "discount_voucher_id": voucher.id,
                "user_id": user.id,
                "redeemed_date": datetime.now(),
            }
        )

        return {"success": _("Successfully redeemed voucher")}

    @http.route(
        ["/go/api/user/voucher/save"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def action_save_voucher(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        voucher = self._get_valid_voucher(data.get("code"))
        if isinstance(voucher, dict) and "error" in voucher:
            return voucher

        saved_user = (
            request.env["voucher.saved.user"]
            .sudo()
            .search(
                [
                    ("discount_voucher_id", "=", voucher.id),
                    ("user_id", "=", user.id),
                ],
                limit=1,
            )
        )
        if saved_user:
            return {"error": _("You have already saved this voucher")}

        request.env["voucher.saved.user"].sudo().create(
            {
                "discount_voucher_id": voucher.id,
                "user_id": user.id,
                "saved_date": datetime.now(),
            }
        )

        return {"success": _("Successfully saved voucher")}

    def _get_voucher_dict(self, voucher):
        """Format voucher object into API dict"""
        return {
            "code": voucher.code,
            "name": voucher.name,
            "discount_value": voucher.discount_value,
            "discount_type": voucher.discount_type,
            "expiry_date": voucher.expiry_date,
            "state": voucher.state,
            "logo": voucher.logo,
        }

    @http.route(
        ["/go/api/user/voucher/save/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_saved_voucher_list(self, **post):
        data = post or self._get_json_request()
        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        saved_vouchers = (
            request.env["voucher.saved.user"].sudo().search([("user_id", "=", user.id)])
        )

        result = []
        for sv in saved_vouchers:
            result.append(self._get_voucher_dict(sv.discount_voucher_id))

        return result

    def _get_valid_voucher_unsaved(self, code):

        if not code:
            return {"error": _("Voucher code is required")}

        voucher = (
            request.env["discount.voucher"]
            .sudo()
            .search([("code", "=", code)], limit=1)
        )
        if not voucher:
            return {"error": _("This Voucher Code is not available")}

        return voucher

    @http.route(
        ["/go/api/user/voucher/unsave"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def action_unsave_voucher(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        voucher = self._get_valid_voucher_unsaved(data.get("code"))
        if isinstance(voucher, dict) and "error" in voucher:
            return voucher

        saved_user = (
            request.env["voucher.saved.user"]
            .sudo()
            .search(
                [("discount_voucher_id", "=", voucher.id), ("user_id", "=", user.id)],
                limit=1,
            )
        )

        if not saved_user:
            return {"error": _("This voucher is not in your saved list")}

        saved_user.sudo().unlink()
        return {"success": _("Successfully removed voucher from your saved list")}

    @http.route(
        ["/go/api/user/voucher/purchase"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def action_purchase_voucher(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        voucher = self._get_valid_voucher(data.get("code"))
        if isinstance(voucher, dict) and "error" in voucher:
            return voucher

        purchased_user = (
            request.env["voucher.purchased.user"]
            .sudo()
            .search(
                [
                    ("discount_voucher_id", "=", voucher.id),
                    ("user_id", "=", user.id),
                ],
                limit=1,
            )
        )

        quantity = int(data.get("quantity") or 1)
        amount_after_discount = data.get("amount_after_discount")

        if purchased_user:
            if purchased_user.payment_status == "Paid":
                return {"success": _("You have Already Purchased Voucher")}

            transaction_id = f"Voucher-{purchased_user.id}"
            skipcash_url = voucher.get_skipcash_url(
                transaction_id, user, quantity, amount_after_discount
            )

            purchased_user.write(
                {
                    "payment_id": skipcash_url.get("id"),
                    "payment_url": skipcash_url.get("pay_url"),
                }
            )
            self._create_skipcash_transaction(purchased_user, skipcash_url)
            return {"skipcash_url": purchased_user.payment_url}

        # Step 4: Create new purchase
        purchased_user = (
            request.env["voucher.purchased.user"]
            .sudo()
            .create(
                {
                    "discount_voucher_id": voucher.id,
                    "user_id": user.id,
                    "purchase_date": datetime.now(),
                    "quantity": quantity,
                    "voucher_price": amount_after_discount,
                }
            )
        )

        self._send_purchase_sms(user, purchased_user)

        transaction_id = f"Voucher-{purchased_user.id}"
        skipcash_url = voucher.get_skipcash_url(
            transaction_id, user, quantity, amount_after_discount
        )

        purchased_user.write(
            {
                "payment_id": skipcash_url.get("id"),
                "payment_url": skipcash_url.get("pay_url"),
            }
        )
        self._create_skipcash_transaction(purchased_user, skipcash_url)

        return {"skipcash_url": skipcash_url.get("pay_url")}

    def _send_purchase_sms(self, user, purchased_user):
        message_provider = request.env["sms.config"].sudo().search([], limit=1)
        if not message_provider:
            return {"error": _("No SMS provider configured")}

        sms_value = {
            "msg_config": message_provider.id,
            "recipient": user.partner_id.phone,
        }

        sms = request.env["sms.message"].sudo().create(sms_value)
        return {"success": True, "sms_id": sms.id}

    def _create_skipcash_transaction(self, purchase, skipcash_url):
        return (
            request.env["skipcash.transaction"]
            .sudo()
            .create(
                {
                    "amount": purchase.total_price,
                    "voucher_purchase_id": purchase.id,
                    "payment_url": skipcash_url.get("pay_url"),
                    "payment_id": skipcash_url.get("id"),
                    "payment_status": "Not Paid",
                }
            )
        )

    @http.route(
        ["/go/api/user/voucher/purchase/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_purchase_voucher_list(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        purchased_vouchers = (
            request.env["voucher.purchased.user"]
            .sudo()
            .search([("user_id", "=", user.id)])
        )

        result = []
        for purchase in purchased_vouchers:
            result.append(self._prepare_purchase_voucher_dict(purchase))

        return result

    def _prepare_purchase_voucher_dict(self, purchase):
        voucher = purchase.discount_voucher_id
        return {
            "code": voucher.code,
            "name": voucher.name,
            "discount_value": voucher.discount_value,
            "discount_type": voucher.discount_type,
            "expiry_date": voucher.expiry_date,
            "payment_status": purchase.payment_status,
            "state": voucher.state,
            "logo": voucher.logo,
            "instruction": (
                voucher.action_convert_html_text(voucher.instruction)
                if voucher.instruction else ""
            ),
        }

    @http.route(
        [
            "/go/api/user/voucher/payment_status",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_voucher_payment_status(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        voucher = self._get_valid_voucher_unsaved(data.get("code"))
        if isinstance(voucher, dict) and "error" in voucher:
            return voucher

        purchased_user = (
            request.env["voucher.purchased.user"]
            .sudo()
            .search(
                [
                    ("discount_voucher_id", "=", voucher.id),
                    ("user_id", "=", user.id),
                ],
                limit=1,
            )
        )
        if not purchased_user:
            return {"error": _("You have not purchased this voucher")}

        return self._prepare_purchase_voucher_payment_dict(purchased_user)

    def _prepare_purchase_voucher_payment_dict(self, purchased_user):
        voucher = purchased_user.discount_voucher_id
        return {
            "code": voucher.code,
            "name": voucher.name,
            "discount_value": voucher.discount_value,
            "discount_type": voucher.discount_type,
            "expiry_date": voucher.expiry_date,
            "terms_condition": voucher.terms_condition,
            "payment_status": purchased_user.payment_status,
            "purchase_date": purchased_user.purchase_date,
            "vis_id": purchased_user.vis_id,
            "payment_id": purchased_user.payment_id,
            "amount": purchased_user.total_price,
            "quantity": purchased_user.quantity,
            "state": voucher.state,
            "logo": voucher.logo,
        }

    @http.route(
        ["/go/api/user/payment/skipcash/return/data"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_skipcash_response_data(self, **post):
        data = post or self._get_json_request()

        if "error" in data:
            return data

        PaymentId = data.get("PaymentId")
        result_obj = self._fetch_skipcash_payment(PaymentId)

        if not result_obj or not isinstance(result_obj, dict):
            return {"error": "Invalid response received from SkipCash API."}

        status_id = result_obj.get("statusId")

        subscription = (
            request.env["subscription.history"]
            .sudo()
            .search([("payment_reference", "=", data.get("TransactionId"))], limit=1)
        )
        if subscription and status_id == 2:
            subscription.payment_state = "paid"
            subscription._compute_is_active()

        self._process_giftcard_payment(PaymentId, status_id, data)

        self._process_voucher_transaction(PaymentId, status_id, data)

    def _fetch_skipcash_payment(self, PaymentId):
        config = request.env["ir.config_parameter"].sudo()
        api_url = config.get_param("go_giftcard.skipcash_api_url")
        authorization_key = config.get_param("go_voucher.skipcash_authorization_key")

        # Validate mandatory credentials
        missing_params = []
        if not api_url:
            missing_params.append("API URL")
        if not authorization_key:
            missing_params.append("Authorization Key")

        if missing_params:
            return {
                "error": f"Missing SkipCash configuration parameters: {', '.join(missing_params)}"
            }

        url = f"{api_url}/v1/payments/{PaymentId}"
        headers = {"Authorization": authorization_key}

        try:
            response = requests.get(url=url, headers=headers)
            if not response or response.status_code != 200:
                return {
                    "error": f"Failed to retrieve SkipCash details for PaymentId: {PaymentId}"
                }

            result_obj = response.json().get("resultObj", {})
            return result_obj

        except Exception as e:
            return {"error": f"Exception while fetching SkipCash payment: {str(e)}"}

    def _process_giftcard_payment(self, PaymentId, status_id, data):
        """Process Gift Card payment if it exists"""
        giftcard = (
            request.env["gift.card"]
            .sudo()
            .search([("payment_id", "=", PaymentId)], limit=1)
        )
        if giftcard and status_id == 2:
            giftcard.vis_id = data.get("VisaId")
            giftcard.payment_status = "Paid"
            giftcard.marked_paid()
            if giftcard.is_cardmoola:
                giftcard.create_cardmoola_order()
            else:
                giftcard.create_order()
            return True
        return False


    def _process_voucher_transaction(self, PaymentId, status_id, data):
        """Process Voucher Purchase transactions if it exists"""
        transaction = (
            request.env["skipcash.transaction"]
            .sudo()
            .search([("payment_id", "=", PaymentId)], limit=1)
        )
        if transaction and status_id == 2:
            transaction.vis_id = data.get("VisaId")
            transaction.payment_status = "Paid"

            purchase = transaction.voucher_purchase_id
            if purchase:
                purchase.vis_id = data.get("VisaId")
                purchase.payment_status = "Paid"

                # Get sender email from config, fallback if not set
                config = request.env["ir.config_parameter"].sudo()
                email_from = (
                    config.get_param("go_voucher.voucher_email_from")
                    or "Golalita<info@golalita.com>"
                )

                template_id = request.env.ref(
                    "go_voucher.voucher_purchased_notification"
                ).sudo()
                template_id.send_mail(
                    purchase.id,
                    force_send=True,
                    email_values={
                        "email_from": email_from,
                        "email_to": purchase.partner_id.email,
                    },
                )
            return True
        return False
