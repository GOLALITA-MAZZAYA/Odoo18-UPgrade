from odoo import http, fields, _
from odoo.http import request
import json
import base64
import logging
_logger = logging.getLogger(__name__)



class Partner(http.Controller):

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

    def _update_partner(self, partner, values):
        update_vals = {
            "name": values.get("business_name") or partner.name,
            "owner_name": values.get("owner_name") or partner.owner_name,
            "email": values.get("email") or partner.email,
            "phone": values.get("phone") or partner.phone,
        }

        logo_status = None
        logo = values.get("logo")
        if logo:
            try:
                if logo.startswith("data:image"):
                    logo = logo.split(",")[1]
                base64.b64decode(logo, validate=True)
                update_vals["image_1920"] = logo
                logo_status = "Logo updated successfully."
            except Exception as e:
                _logger.warning("Logo is not valid base64: %s", e)
                logo_status = "Logo not updated, invalid base64."

        partner.sudo().write(update_vals)

        return {"logo_status": logo_status}

    def _upload_attachment(self, partner, file_data, filename):
        if file_data:
            request.env["ir.attachment"].sudo().create(
                {
                    "name": filename,
                    "type": "binary",
                    "datas": file_data,
                    "res_model": "res.partner",
                    "res_id": partner.id,
                }
            )

    def _create_branches(self, partner, branches):
        for b in branches or []:
            if b.get("branch_name") and b.get("location"):
                request.env["res.partner"].sudo().create(
                    {
                        "name": b["branch_name"],
                        "parent_id": partner.id,
                        "type": "branch",
                        "street": b["location"],
                    }
                )

    @http.route(
        "/go/api/vendor/update_profile",
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
    )
    def update_vendor_profile(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        partner = user.partner_id
        self._update_partner(partner, data)

        self._upload_attachment(partner, data.get("cr_copy"), "CR Copy")
        self._upload_attachment(partner, data.get("trade_license"), "Trade License")
        self._upload_attachment(
            partner, data.get("vendor_terms"), "Signed Vendor Terms"
        )

        self._create_branches(partner, data.get("branches"))

        return {
            "status": "success",
            "message": _("Vendor profile updated successfully"),
        }
