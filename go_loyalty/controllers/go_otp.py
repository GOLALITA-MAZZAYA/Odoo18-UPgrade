import json

from odoo.http import request

from odoo import http, fields, _


class GoOTP(http.Controller):
    def _validate_token(self, data):
        token = data.get("token")
        if not token:
            return {"error": _("Token is missing")}
        user = request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
        if not user:
            return {"error": _("Invalid User Token")}
        return user

    def _get_user_by_phone(self, data):
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

    def _get_user_by_phone_or_email(self, data):
        phone = data.get("phone")
        if not phone and data.get("otp_by") == "phone":
            return {"error": _("Phone number is missing")}
        email = data.get("email")
        if not email and data.get("otp_by") == "email":
            return {"error": _("Email is missing")}
        user = (
            (
                request.env["res.users"]
                .sudo()
                .search([("partner_id.phone", "=", phone)], limit=1)
            )
            if data.get("otp_by") == "phone"
            else (
                request.env["res.users"].sudo().search([("login", "=", email)], limit=1)
            )
        )
        if not user:
            return {"error": _("No user found with this phone number")}
        return user

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

    @http.route(
        ["/go/api/send/otp"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_send_otp(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._get_user_by_phone_or_email(data)
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

    @http.route(
        "/go/api/otp/verify/new_user",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_otp_verify_new_user(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            phone = data.get("phone")
            otp = data.get("otp")

            if not phone:
                return {"error": _("Phone number is missing")}
            if not otp:
                return {"error": _("OTP is required")}

            current_user = (
                request.env["res.users"]
                .sudo()
                .search([("partner_id.phone", "=", phone)], limit=1)
            )

            if not current_user:
                return {"error": _("Your phone number is not registered with us.")}

            verify = (
                request.env["user.otp"].sudo().is_valid_otp(current_user.login, otp)
            )

            if not verify:
                return {"error": _("Invalid OTP")}

            token = request.env["res.users"].sudo().get_user_access_token()
            current_user.sudo().write({"token": token})

            return {"success": _("OTP verified successfully"), "token": token}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/otp/verify"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_otp_verify(self, **post):
        try:
            data = post or self._get_json_request()
            current_user = False

            if data.get("email"):
                current_user = (
                    request.env["res.users"]
                    .sudo()
                    .search([("partner_id.email", "=", data.get("email"))], limit=1)
                )
            if data.get("phone"):
                current_user = (
                    request.env["res.users"]
                    .sudo()
                    .search([("partner_id.phone", "=", data.get("phone"))], limit=1)
                )

            if not current_user:
                return {
                    "error": _("Your email/phone number is not registered with us.")
                }

            if not data.get("otp"):
                return {"error": _("otp is required")}

            verify = (
                request.env["user.otp"]
                .sudo()
                .is_valid_otp(current_user.login, data.get("otp"))
            )

            if not verify:
                return {"error": _("Invalid OTP")}

            token = request.env["res.users"].get_user_access_token()
            current_user.token = token
            return {"success": "Otp Verify Successfully", "token": token}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/create/otp/password"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_api_create_otp_password(self, **post):
        try:
            try:
                data = post or self._get_json_request()
                if not isinstance(data, dict):
                    return {"error": "Invalid JSON format", "status_code": "01"}
            except Exception:
                return {"error": "Malformed JSON payload", "status_code": "01"}

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user
            if not current_user:
                return {"error": "Invalid User Token", "status_code": "01"}

            new_password = data.get("new_password")
            if not new_password:
                return {"error": "Password missing", "status_code": "01"}

            current_user.sudo().write({"password": new_password})
            return {"message": "Successfully changed password", "status_code": "00"}

        except Exception as e:
            return {"error": "Something went wrong: %s" % str(e), "status_code": "01"}

    @http.route(
        [
            "/go/api/send/otp/email/<string:org_type>",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_send_otp_email_string(self, org_type, **post):
        try:
            data = post or self._get_json_request()
            if not isinstance(data, dict):
                return {"error": "Invalid JSON format", "status_code": "01"}
        except Exception:
            return {"error": "Malformed JSON payload", "status_code": "01"}

        email = data.get("email")
        if not email:
            return {"error": _("Email is missing")}
        domain = [
            ("partner_id.org_type", "=", org_type),
            ("partner_id.email", "=", email),
        ]
        current_user = request.env["res.users"].sudo().search(domain, limit=1)

        if not current_user:
            return {"error": _("Your email number is not registered with us.")}

        is_sent = (
            request.env["user.otp"]
            .sudo()
            .generate_and_send_otp_email(current_user.login, post.get("email"))
        )
        if not is_sent:
            return {"error": _("Could not send otp! either email is invalid")}

        return {
            "success": "Otp has been successfully sent and will be valid for 5 minutes."
        }
