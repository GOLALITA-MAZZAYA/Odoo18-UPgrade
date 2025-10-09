from odoo import http, fields, _
from odoo.http import request
import json


class User(http.Controller):

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
        [
            "/go/api/user/archive",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_archive(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner = current_user.partner_id
        current_user.sudo().unlink()
        partner.sudo().unlink()

        return {"success": _("User deleted successfully")}

    @http.route(
        [
            "/go/api/user/account/delete",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_new_delete(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner = current_user.partner_id
        current_user.sudo().unlink()
        partner.sudo().unlink()

        return {"success": _("User deleted successfully")}

    @http.route(
        [
            "/go/api/user/account/alldelete/",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_all_delete(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        emails = data.get("emails")
        if not emails or not isinstance(emails, list):
            return {"error": _("A list of email IDs is required")}

        deleted_users = []
        errors = []

        for email in emails:
            user = (
                request.env["res.users"].sudo().search([("login", "=", email)], limit=1)
            )
            if not user:
                errors.append(f"User with email {email} not found")
                continue
            partner = user.partner_id
            try:
                user.sudo().unlink()
                if partner:
                    partner.sudo().unlink()
                deleted_users.append(email)
            except Exception as e:
                errors.append(f"Error deleting user with email {email}: {str(e)}")

        return {
            "success": _("User(s) deleted successfully"),
            "deleted_users": deleted_users,
            "errors": errors or None,
        }

    @http.route(
        [
            "/go/api/user/detail/email",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_detail_by_email(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner = current_user.partner_id
        return {
            "success": _("User Details"),
            "email": partner.email,
            "name": partner.name,
            "id": partner.id,
            "family_head_id": partner.id,
            "tracking_partner_id": partner.id,
            "paused_notification": "false",
            "token": data.get("token"),
        }

    @http.route(
        [
            "/go/api/user/verify/phone",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_verify_phone(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner = current_user.partner_id
        if partner:
            partner.sudo().write({"phone_verified": True})
            return {"success": _("Phone Verified Successfully")}

        return {"error": _("No Partner Found for User")}

    @http.route(
        ["/go/api/user/add/members"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_add_family_members(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner_id = current_user.partner_id
        if partner_id.entity_type != "employee":
            return {"error": _("You must be employee of organisation to add members")}

        required_fields = ["password", "phone", "email"]
        for field in required_fields:
            if not data.get(field):
                return {"error": _(f"{field} missing")}

        try:
            partner_vals = {
                "name": data.get("name"),
                "moi_last_name": data.get("last_name"),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "parent_id": partner_id.parent_id.id,
                "family_head_member_id": partner_id.id,
                "org_type": partner_id.org_type,
                "user_expiry": partner_id.user_expiry,
                "entity_type": "employee",
                "image_1920": data.get("image_1920", False),
            }
            new_partner = request.env["res.partner"].sudo().create(partner_vals)
        except Exception as e:
            return {"error": _("Failed to create partner: %s") % str(e)}

        try:
            user_vals = {
                "name": new_partner.name,
                "partner_id": new_partner.id,
                "email": data.get("email"),
                "login": data.get("email"),
                "password": data.get("password"),
            }
            new_user = request.env["res.users"].sudo()._signup_create_user(user_vals)
        except Exception as e:
            new_partner.sudo().unlink()
            return {"error": _("Failed to create user: %s") % str(e)}

        return {"success": _("Family member has been created successfully")}

    # @http.route(
    #     ["/go/api/user/remove/members"],
    #     auth="public",
    #     website=True,
    #     methods=["POST"],
    #     csrf=False,
    #     type="json",
    # )
    # def go_user_delete_family_members(self, **post):
    #     data = post or self._get_json_request()
    #     if "error" in data:
    #         return data
    #
    #     current_user = self._validate_token(data)
    #     if isinstance(current_user, dict):
    #         return current_user
    #
    #     partner_id = current_user.partner_id
    #     if partner_id.entity_type != "employee":
    #         return {
    #             "error": _("You must be employee of organisation to remove members")
    #         }
    #
    #     family_user_id = data.get("family_user_id")
    #     if not family_user_id:
    #         return {"error": _("Invalid Family ID")}
    #
    #     family_partner = (
    #         request.env["res.partner"]
    #         .sudo()
    #         .search([("id", "=", family_user_id)], limit=1)
    #     )
    #     if not family_partner:
    #         return {"error": _("Family member not found")}
    #
    #     try:
    #         family_user = (
    #             request.env["res.users"]
    #             .sudo()
    #             .search([("partner_id", "=", family_partner.id)], limit=1)
    #         )
    #         if family_user:
    #             family_user.sudo().unlink()
    #     except Exception as e:
    #         return {"error": _("Failed to delete user: %s") % str(e)}
    #
    #     try:
    #         family_partner.sudo().unlink()
    #     except Exception as e:
    #         return {"error": _("Failed to delete partner: %s") % str(e)}
    #
    #     return {"success": _("Family member has been deleted successfully")}

    @http.route(
        [
            "/go/api/user/delete/members",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_remove_family_members(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner_id = current_user.partner_id
        if partner_id.entity_type != "employee":
            return {
                "error": _("You must be employee of organisation to remove members")
            }

        family_user_id = data.get("family_user_id")
        if not family_user_id:
            return {"error": _("Member ID Missing")}

        family_partner = (
            request.env["res.partner"]
            .sudo()
            .search(
                [
                    ("parent_id", "=", partner_id.parent_id.id),
                    ("id", "=", family_user_id),
                ],
                limit=1,
            )
        )

        if not family_partner:
            return {"error": _("Family member not found in system")}

        try:
            users = family_partner.user_ids
            if users:
                users.sudo().write({"active": False})
            family_partner.sudo().write({"active": False})
        except Exception as e:
            return {"error": _("Failed to remove family member: %s") % str(e)}

        return {"success": _("Family member has been removed successfully")}
