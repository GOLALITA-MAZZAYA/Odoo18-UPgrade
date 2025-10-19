import base64

from odoo.exceptions import UserError
from odoo.http import request, route

# import magic
from odoo import SUPERUSER_ID, _, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as OAuthSignupHome

from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
import json

SECRET_KEY = "e9e6b0138afe1c861d7c9d3af96e33d3"


class AuthSignupHome(OAuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in "entity_type"}
        result = super()._prepare_signup_values(qcontext)
        if values.get("entity_type") in ["merchant", "organisation"]:
            result["company_type"] = "company"
        return result


class GoMain(http.Controller):

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
        ["/organisation/employee/registration/v2"],
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def organisation_employee_signup_v2(self, **kwargs):
        try:
            data = kwargs or self._get_json_request()
            if isinstance(data, dict) and data.get("error"):
                return data

            required_fields = ["parent_id", "email", "password", "name", "phone"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {
                    "error": _("Missing required fields: %s")
                    % ", ".join(missing_fields)
                }

            org = request.env["res.partner"].sudo().browse(int(data["parent_id"]))
            if not org.exists():
                return {"error": _("Invalid organization ID")}

            if org.need_registration_code:
                code = data.get("code")
                if not code:
                    return {"error": _("Registration Code missing")}
                if not org._is_code_exist(code):
                    return {"error": _("Invalid Registration Code")}
                if org._is_registred(code):
                    return {"error": _("User is already registered with this code")}

            partner_vals = {
                "name": data["name"],
                "last_name": data.get("last_name", ""),
                "login": data["email"],
                "password": data["password"],
                "email": data["email"],
                "entity_type": "employee",
                "phone": data["phone"],
                "parent_id": int(data["parent_id"]),
            }

            request.env["res.users"].sudo().signup(partner_vals, False)

            partner = org.child_ids.filtered(
                lambda c: c.email == data["email"] and c.phone == data["phone"]
            )
            if not partner:
                return {"error": _("User registration failed — partner not found")}

            partner.org_type = "golalita"
            partner.user_expiry = datetime.now() + timedelta(days=365)

            if org.need_registration_code and data.get("code"):
                org.assign_registration_code(data["code"], partner.id)

            return {
                "status": True,
                "message": _("Employee registered successfully"),
                "partner_id": partner.id,
                "org": org,
            }
        except Exception as e:
            _logger.exception("Error during employee signup: %s", e)
            return {"error": _("Something went wrong. Please try again later.")}

    @http.route(
        ["/organisation/employee/registration/v3"],
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def organisation_employee_signup_v3(self, **kwargs):
        try:
            data = kwargs or self._get_json_request()
            if isinstance(data, dict) and data.get("error"):
                return data

            required_fields = ["parent_id", "email", "password", "name", "phone"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {
                    "error": _("Missing required fields: %s")
                    % ", ".join(missing_fields)
                }

            org = request.env["res.partner"].sudo().browse(int(data["parent_id"]))
            if not org.exists():
                return {"error": _("Invalid organization ID")}

            if org.need_registration_code:
                code = data.get("code")
                if not code:
                    return {"error": _("Registration Code missing")}
                if not org._is_code_exist(code):
                    return {"error": _("Invalid Registration Code")}
                if org._is_registred(code):
                    return {"error": _("User is already registered with this code")}

            partner_vals = {
                "name": data["name"],
                "last_name": data.get("last_name", ""),
                "login": data["email"],
                "password": data["password"],
                "email": data["email"],
                "entity_type": "employee",
                "phone": data["phone"],
                "parent_id": int(data["parent_id"]),
            }

            request.env["res.users"].sudo().signup(partner_vals, False)

            if org.need_registration_code and data.get("code"):

                partner = org.child_ids.filtered(
                    lambda c: c.email == data["email"] and c.phone == data["phone"]
                )
                org.assign_registration_code(data["code"], partner.id)

            return {
                "status": True,
                "message": _("Employee registered successfully"),
                "org": org,
            }

        except Exception as e:
            _logger.exception("Error during employee signup: %s", e)
            return {"error": _("Something went wrong. Please try again later.")}

    @http.route(
        ["/organisation/employee/registration/v2/<path:org_type>"],
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def organisation_employee_signup_v2_org(self, org_type="golalita", **post):
        try:
            org_key = org_type.replace("/", "").lower()

            ORG_MAP = {
                "golalita": "golalita",
                "fekrtycard": "golalita",
                "qlm": "qlm",
                "qib": "qatarinsurance",
                "masrif": "masrif",
                "beema": "beema",
                "alzamanexchange": "alzamanexchange",
                "barwa": "barwa",
                "daam": "daam",
                "sjc": "sjc",
                "gulfexchange": "gulfexchange",
                "rcodegulfexchange": "gulfexchange",
                "qatar_poststop": "qatar_post",
                "hayyakamstopana": "hayyakam",
                "moiaa": "moi",
                "moi": "moi",
            }

            org_name = ORG_MAP.get(org_key, None)

            if org_name is None:
                return {"error": _("Invalid organization type")}

            data = post or self._get_json_request()
            if isinstance(data, dict) and data.get("error"):
                return data

            required_fields = ["parent_id", "email", "password", "name", "phone"]
            if org_name == "qlm":
                required_fields.append("x_qid")
            if org_name == "moi":
                required_fields.extend(
                    ["first_name_arbic", "barcode", "x_last_name_arbic",
                     "x_moi_last_name", "card_number"]
                )
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {
                    "error": _("Missing required fields: %s")
                    % ", ".join(missing_fields)
                }

            org = request.env["res.partner"].sudo().browse(int(data["parent_id"]))
            if not org.exists():
                return {"error": _("Invalid organization ID")}

            if org.need_registration_code:
                code = data.get("code")
                if not code:
                    return {"error": _("Registration Code missing")}
                if not org._is_code_exist(code):
                    return {"error": _("Invalid Registration Code")}
                if org._is_registred(code):
                    return {"error": _("User is already registered with this code")}

            barcode = data.get("card_number").replace("-", "")
            partner_vals = {
                "name": data["name"],
                "last_name": data.get("last_name", ""),
                "login": data["email"],
                "password": data["password"],
                "email": data["email"],
                "entity_type": "employee",
                "phone": data["phone"],
                "parent_id": int(data["parent_id"]),
                "qid": data.get("x_qid", "") if org_type == "qlm" else "",
            }
            if org_name == "moi":
                partner_vals.update(
                    {
                        "first_name_arbic": data.get("first_name_arbic", ""),
                        "last_name_arbic": data.get("last_name_arbic", ""),
                        "barcode": barcode,
                    }
                )

            request.env["res.users"].sudo().signup(partner_vals, False)

            partner = org.child_ids.filtered(
                lambda c: c.email == data["email"] and c.phone == data["phone"]
            )
            if not partner:
                return {"error": _("User registration failed — partner not found")}

            partner.org_type = org_name or "golalita"
            partner.user_expiry = datetime.now() + timedelta(days=365)

            if org.need_registration_code and data.get("code"):
                org.assign_registration_code(data["code"], partner.id)
                if org_name == "moi" and org._is_vip(data["code"]):
                    partner.employee_type = "vip"
                else:
                    partner.employee_type = "standard"

            return {
                "status": True,
                "message": _("Employee registered successfully"),
                "partner_id": partner.id,
                "org": org,
            }

        except Exception as e:
            _logger.exception("Error during employee signup: %s", e)
            return {"error": _("Something went wrong. Please try again later.")}

    @http.route(
        ["/organisation/customer/registration/V2"],
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def organisation_customer_signup_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if isinstance(data, dict) and data.get("error"):
                return data

            required_fields = ["parent_id", "email", "password", "name", "phone"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {
                    "error": _("Missing required fields: %s")
                    % ", ".join(missing_fields)
                }

            org = request.env["res.partner"].sudo().browse(int(data["parent_id"]))
            if not org.exists():
                return {"error": _("Invalid organization ID")}

            if org.need_registration_code:
                code = data.get("code")
                if not code:
                    return {"error": _("Registration Code missing")}
                if not org._is_code_exist(code):
                    return {"error": _("Invalid Registration Code")}
                if org._is_registred(code):
                    return {"error": _("User is already registered with this code")}

            partner_vals = {
                "name": data["name"],
                "last_name": data.get("last_name", ""),
                "login": data["email"],
                "password": data["password"],
                "email": data["email"],
                "entity_type": "employee",
                "phone": data["phone"],
                "parent_id": int(data["parent_id"]),
            }

            request.env["res.users"].sudo().signup(partner_vals, False)

            partner = org.child_ids.filtered(
                lambda c: c.email == data["email"] and c.phone == data["phone"]
            )
            if not partner:
                return {"error": _("User registration failed — partner not found")}

            partner.user_expiry = datetime.now() + timedelta(days=365)

            if org.need_registration_code and data.get("code"):
                org.assign_registration_code(data["code"], partner.id)

            return {
                "status": True,
                "message": _("Employee registered successfully"),
                "partner_id": partner.id,
                "org": org,
            }

        except Exception as e:
            _logger.exception("Error during employee signup: %s", e)
            return {"error": _("Something went wrong. Please try again later.")}
