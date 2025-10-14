from odoo import http, fields, _
from odoo.http import request
import json
from werkzeug.urls import url_join


class User(http.Controller):

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

    def _prepare_partner_update_vals(self, data):
        fields_map = {
            "name": "name",
            "last_name": "moi_last_name",
            "phone": "phone",
            "email": "email",
            "relation_type": "relation_type",
        }
        vals = {}
        for key, field in fields_map.items():
            value = data.get(key)
            if value:
                vals[field] = value
        return vals

    def _get_user_org_profile(self, partner, web_base_url):
        return {
            "org_name": partner.name,
            "phone": partner.phone,
            "email": partner.email,
            "website": partner.website,
            "barcode": partner.barcode,
            "address": partner.contact_address,
            "partner_latitude": partner.partner_latitude,
            "partner_longitude": partner.partner_longitude,
            "description": partner.merchant_details_en,
            "rating": partner.merchant_rating,
            "notes": partner.comment,
            "whatsapp_enabled": partner.enable_whatsapp,
            "whatsapp_title": partner.whatsapp_title,
            "whatsapp_number": partner.whatsapp_number,
            "whatsappx_prefill_message": partner.whatsapp_prefill_message,
            "map_banner": url_join(
                web_base_url, f"/go/api/image/{partner.id}/map_banner/res.partner"
            ),
            "org_logo": url_join(
                web_base_url, f"/go/api/image/{partner.id}/image_512/res.partner"
            ),
        }

    # def _get_user_merchant_profile(self, partner, web_base_url):
    #     try:
    #         products = self._get_products(partner)
    #         banners = self._get_banners(partner, web_base_url)
    #         offer_products = self._get_offer_products(partner)
    #
    #         return {
    #             "merchant_name": partner.name,
    #             "merchant_name_arabic": partner.x_arabic_name,
    #             "x_for_employee_type": partner.x_for_employee_type,
    #             "phone": partner.phone,
    #             "email": partner.email,
    #             "website": partner.website,
    #             "merchant_code": partner.barcode,
    #             "open_from": partner.x_open_from,
    #             "open_till": partner.x_open_till,
    #             "address": partner.contact_address,
    #             "partner_latitude": partner.partner_latitude,
    #             "partner_longitude": partner.partner_longitude,
    #             "ribbon_text": partner.ribbon_text,
    #             "x_ribbon_text_arabic": partner.x_ribbon_text_arabic,
    #             "ribbon_color": partner.ribbon_color,
    #             "ribbon_position": partner.ribbon_position,
    #             "description": partner.merchant_details,
    #             "description_arabic": partner.x_merchant_details_ar,
    #             "description_masrif": partner.x_merchant_details_masrif,
    #             "description_masrif_arabic": partner.x_merchant_details_masrif_ar,
    #             "x_online_store": partner.x_online_store,
    #             "rating": partner.merchant_rating,
    #             "notes": partner.comment,
    #             "map_banner": url_join(
    #                 web_base_url, f"/go/api/image/{partner.id}/map_banner/res.partner"
    #             ),
    #             "merchant_logo": url_join(
    #                 web_base_url, f"/go/api/image/{partner.id}/image_512/res.partner"
    #             ),
    #             "category": (
    #                 partner.partner_category_id.name
    #                 if partner.partner_category_id
    #                 else ""
    #             ),
    #             "category_logo": (
    #                 url_join(
    #                     web_base_url,
    #                     f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
    #                 )
    #                 if partner.partner_category_id
    #                 else ""
    #             ),
    #             "banners": banners,
    #             "products": products,
    #             "is_hotel": partner.is_hotel_type,
    #             "x_kts": partner.x_kts,
    #             "offer_products": offer_products,
    #             "whatsapp_enabled": partner.enable_whatsapp,
    #             "whatsapp_title": partner.whatsapp_title,
    #             "whatsapp_number": partner.whatsapp_number,
    #             "whatsappx_prefill_message": partner.whatsapp_prefill_message,
    #             "pdf_attached": partner.x_pdf_attached,
    #             "company_contract_url": url_join(
    #                 web_base_url, f"/web/binary/contract_download_pdf/{partner.id}"
    #             ),
    #             "company_registartion_url": url_join(
    #                 web_base_url, f"/web/binary/registration_download_pdf/{partner.id}"
    #             ),
    #             "x_terms_condition": partner.x_terms_condition,
    #             "x_terms_condition_arabic": partner.x_terms_condition_arabic,
    #             "x_terms_condition_new": partner.terms_conditions_en,
    #             "x_terms_condition_arabic_new": partner.terms_conditions_ar,
    #             "x_moi_show": partner.show_in_moi,
    #             "x_contact_number_ar": partner.ar_contact_number,
    #             "x_email_ar": partner.ar_email,
    #             "x_street_ar": partner.ar_street,
    #             "x_city_ar": partner.ar_city,
    #             "x_country_ar": partner.ar_country,
    #             "x_time_from_ar": partner.ar_time_from,
    #             "x_time_to_ar": partner.ar_time_to,
    #             "gpoint": partner.go_loyalty_point,
    #         }
    #     except Exception as e:
    #         return {"error": _("Failed to fetch merchant profile: %s") % str(e)}
    #
    # def _get_banners(self, partner, web_base_url):
    #     try:
    #         banners = (
    #             request.env["merchant.banner"]
    #             .sudo()
    #             .search_read(
    #                 [("partner_id", "=", partner.id)],
    #                 ["name", "merchant_rating", "x_sequence"],
    #             )
    #         )
    #         for banner in banners:
    #             banner["banner_image"] = url_join(
    #                 web_base_url,
    #                 f'/go/api/image/{banner["id"]}/image_1920/merchant.banner',
    #             )
    #         return banners
    #     except Exception as e:
    #         return []
    #
    # def _get_products(self, partner):
    #     try:
    #         return (
    #             request.env["product.template"]
    #             .sudo()
    #             .search_read(
    #                 [("merchant_id", "=", partner.id), ("is_in_offer", "=", False)],
    #                 [
    #                     "name",
    #                     "image_url",
    #                     "lst_price",
    #                     "list_price",
    #                     "x_arabic_name",
    #                     "discount",
    #                     "x_point",
    #                     "offer_label",
    #                     "default_code",
    #                     "barcode",
    #                     "description",
    #                     "description_sale",
    #                 ],
    #             )
    #         )
    #     except Exception as e:
    #         return []
    #
    # def _get_offer_products(self, partner):
    #     try:
    #         return (
    #             request.env["product.template"]
    #             .sudo()
    #             .search_read(
    #                 [("merchant_id", "=", partner.id), ("is_in_offer", "=", True)],
    #                 [
    #                     "name",
    #                     "image_url",
    #                     "lst_price",
    #                     "list_price",
    #                     "x_arabic_name",
    #                     "discount",
    #                     "x_point",
    #                     "offer_label",
    #                     "default_code",
    #                     "barcode",
    #                     "description",
    #                     "description_sale",
    #                     "start_date",
    #                     "end_date",
    #                     "min_quantity",
    #                     "max_quantity",
    #                     "x_offer_type",
    #                     "x_offer_type_discount",
    #                     "x_offer_type_promo_code",
    #                     "x_merchant_online_store",
    #                     "x_buy_link",
    #                 ],
    #             )
    #         )
    #     except Exception as e:
    #         return []

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

    @http.route(
        ["/go/api/user/update/members"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_update_family_members(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner_id = current_user.partner_id
        if partner_id.entity_type != "employee":
            return {
                "error": _("You must be employee of organisation to update members")
            }

        member_id = data.get("member_id")
        if not member_id:
            return {"error": _("Member ID Missing")}

        partner = (
            request.env["res.partner"]
            .sudo()
            .search(
                [("parent_id", "=", partner_id.parent_id.id), ("id", "=", member_id)],
                limit=1,
            )
        )
        if not partner:
            return {"error": _("Family member not found in system")}

        vals_to_update = self._prepare_partner_update_vals(data)

        try:
            if vals_to_update:
                partner.sudo().write(vals_to_update)
            if data.get("password") and partner.user_ids:
                partner.user_ids[0].sudo().write({"password": data["password"]})
        except Exception as e:
            return {"error": _("Failed to update family member: %s") % str(e)}

        return {"success": _("Family member details have been updated successfully")}

    # @http.route(
    #     ["/go/api/user/merchant/details"],
    #     auth="public",
    #     website=True,
    #     methods=["POST"],
    #     csrf=False,
    #     type="json",
    #     cors="*",
    # )
    # def get_user_merchant_details(self, **post):
    #     try:
    #         data = post or self._get_json_request()
    #         if "error" in data:
    #             return data
    #
    #         user = self._validate_token(data)
    #         if isinstance(user, dict) and "error" in user:
    #             return user
    #
    #         merchant_id = data.get("merchant_id")
    #         if not merchant_id:
    #             return {"error": _("Merchant ID Missing")}
    #
    #         merchant = request.env["res.partner"].sudo().browse(merchant_id)
    #         if not merchant.exists():
    #             return {"error": _("Merchant not found")}
    #         if merchant.entity_type != "merchant":
    #             return {"error": _("Provided merchant is not registered with us")}
    #
    #         web_base_url = (
    #             request.env["ir.config_parameter"].sudo().get_param("web.base.url")
    #         )
    #         return self._get_user_merchant_profile(merchant, web_base_url)
    #
    #     except Exception as e:
    #         return {
    #             "error": _("Unexpected error while fetching merchant details: %s")
    #             % str(e)
    #         }

    @http.route(
        ["/go/api/user/org/details"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_org_details(self, **post):
        try:
            data = post or self._get_json_request()
            if not data.get("token"):
                return {"error": _("Invalid User Token")}

            current_user = (
                request.env["res.users"]
                .sudo()
                .search([("token", "=", data["token"])], limit=1)
            )
            if not current_user:
                return {"error": _("Invalid User Token")}

            org_id = data.get("org_id")
            if not org_id:
                return {"error": _("Org ID Missing")}

            organisation = request.env["res.partner"].sudo().browse(org_id)
            if organisation.entity_type != "organisation":
                return {"error": _("Provided Org. is not registered with us")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            return self._get_user_org_profile(organisation, web_base_url)

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/user/org/lists/v3"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_org_list(self, **post):
        try:
            data = post or self._get_json_request()
            if not data.get("token"):
                return {"error": _("Invalid User Token")}

            current_user = (
                request.env["res.users"]
                .sudo()
                .search([("token", "=", data["token"])], limit=1)
            )
            if not current_user:
                return {"error": _("Invalid User Token")}

            domain = [
                ("entity_type", "=", "organisation"),
                ("reg_hide", "=", False),

            ]
            if data.get("category_id"):
                domain.append(("partner_category_id", "=", data["category_id"]))
            if data.get("merchant_type"):
                domain.append(("merchant_type", "=", data["merchant_type"]))

            organisations = request.env["res.partner"].sudo().search(domain)
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            res = []

            for org in organisations:
                res.append(
                    {
                        "org_name": org.name,
                        "org_id": org.id,
                        "x_sequence": org.sequence,
                        "need_code": org.need_registration_code,
                        "barcode": org.barcode,
                        "org_latitude": org.partner_latitude,
                        "org_longitude": org.partner_longitude,
                        "rating": org.merchant_rating,
                        "org_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{org.id}/image_512/res.partner",
                        ),
                        "org_banner": url_join(
                            web_base_url,
                            f"/go/api/image/{org.id}/map_banner/res.partner",
                        ),
                    }
                )

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/user/save/offers/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_api_save_offers_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            response = [{"status": "Offer Saved Successfully"}]
            return response

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}
