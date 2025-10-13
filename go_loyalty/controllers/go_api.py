from odoo import http, fields, _
from odoo.http import request
import json


class GoApi(http.Controller):

    @staticmethod
    def _validate_token(data):
        token = data.get("token")
        if not token:
            return {"error": _("Token is missing")}
        user = request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
        if not user:
            return {"error": _("Invalid User Token")}
        return user

    @staticmethod
    def _get_user_by_phone(data):
        phone = data.get("phone")
        if not phone:
            return {"error": _("Phone number is missing")}
        user = (
            request.env["res.users"]
            .sudo()
            .search([("partner_id.phone", "=", phone)], limit=1)
        )
        if not user:
            return {"error": _("No user found with this phone number")}
        return user

    @staticmethod
    def _get_json_request():
        try:
            if not request.httprequest.data:
                return {"error": _("No JSON payload provided")}
            data = json.loads(request.httprequest.data.decode("utf-8"))
            if not isinstance(data, dict):
                return {"error": _("Invalid JSON format")}
            return data
        except json.JSONDecodeError:
            return {"error": _("Malformed JSON payload")}

    @http.route(
        ["/go/api/send/otp/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_send_otp_v2(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._get_user_by_phone(data)
        if isinstance(user, dict):
            return user

        try:
            is_sent = (
                request.env["user.otp"]
                .sudo()
                .generate_and_send_otp(user.login, user.partner_id.phone)
            )
            if not is_sent:
                return {
                    "error": _("Could not send OTP! Either phone number is invalid.")
                }
        except Exception as e:
            return {"error": _("Failed to send OTP: %s") % str(e)}

        return {
            "success": _(
                "OTP has been successfully sent and will be valid for 5 minutes."
            )
        }
