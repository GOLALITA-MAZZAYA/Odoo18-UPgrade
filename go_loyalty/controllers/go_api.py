import json
from datetime import datetime

from odoo.http import request

from odoo import http, fields, _


class GoApi(http.Controller):

    def _validate_token(self, data):
        token = data.get("token")
        if not token:
            return {"error": _("Token is missing")}
        user = request.env["res.users"].sudo().search([("token", "=", token)], limit=1)
        if not user:
            return {"error": _("Invalid User Token")}
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
        ["/go/api/send/mail/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def send_mail_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = {
                "customer_name": "Customer Information Missing",
                "customer_id": "Customer ID Missing",
                "customer_email": "Email Missing",
                "customer_phone": "Phone No. Missing",
                "track_type": "Tracking Type Missing",
                "track_value": "Track Value Missing",
                "track_date_time": "Date Time Missing",
            }

            for field, message in required_fields.items():
                if not data.get(field):
                    return {"error": _(message)}

            possible_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y %H:%M",
                "%d-%m-%Y %I:%M %p",
                "%Y-%m-%d",
            ]

            parsed_date = None
            for fmt in possible_formats:
                try:
                    parsed_date = datetime.strptime(data.get("track_date_time"), fmt)
                    break
                except Exception:
                    continue

            if not parsed_date:
                return {
                    "error": _("Invalid date format. Please use a supported format.")
                }

            partner = (
                request.env["res.partner"]
                .sudo()
                .search([("id", "=", data.get("customer_id"))], limit=1)
            )
            if not partner:
                return {"error": _("Customer not found in the system")}

            track = (
                request.env["track.list"]
                .sudo()
                .create(
                    {
                        "customer_name": data.get("customer_name"),
                        "customer_email": data.get("customer_email"),
                        "customer_id": data.get("customer_id"),
                        "customer_phone": data.get("customer_phone"),
                        "track_value": data.get("track_value"),
                        "track_type": data.get("track_type"),
                        "track_date_time": parsed_date,
                    }
                )
            )

            track.action_send_mail_track()

            # email_body = f"""
            #     Dear {data.get('customer_name')},<br><br>
            #     Thanks for using Golalita Application!<br><br>
            #     Kindly use the below Promo-code to avail the offer on Golalita Merchant's Network.<br><br>
            #     <b>Promo-Code:</b> {data.get('track_value')}<br><br>
            #     <i>Golalita Team</i>
            # """

            # mail_vals = {
            #     "subject": "Thanks for using Golalita",
            #     "body_html": email_body,
            #     "email_to": data.get("customer_email"),
            #     "auto_delete": False,
            #     "email_from": "support@golalita.com",
            # }

            # mail = request.env['mail.mail'].sudo().create(mail_vals)
            # mail.sudo().send()

            return {
                "success": _("Tracking updated successfully !!"),
                "tracking_id": track.id,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/transfer/points",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_transfer_points(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            phone = data.get("phone")
            points = data.get("points")

            if not phone or not points:
                return {"error": _("Mobile Number and Points are required")}

            partner_from = current_user.partner_id
            partner_to = (
                request.env["res.partner"]
                .sudo()
                .search([("phone", "=", phone)], limit=1)
            )

            if not partner_to:
                return {
                    "error": _(
                        "Destination user not found. Please enter a valid mobile number."
                    )
                }

            transfer = (
                request.env["loyalty.point.transfer"]
                .sudo()
                .create(
                    {
                        "from_id": partner_from.id,
                        "to_id": partner_to.id,
                        "points": points,
                    }
                )
            )
            transfer.action_transfer()

            return {"success": _("Points have been successfully transferred.")}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}
