from odoo import http, fields, _
from odoo.http import request
import json
import ast
import requests
from werkzeug.urls import url_join
BEARER_TOKEN = "l3UIiRwXb0oZPfAeQqY2Hk3l"
import logging
_logger = logging.getLogger(__name__)
SECRET_KEY = "da6108c364cbab86dc2eaa200588489e1765fd58da78afbbd3c687e8ddf0a763"

import hmac
import hashlib
import base64


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

    def _get_banners(self, partner, web_base_url):
        try:
            banners = (
                request.env["merchant.banner"]
                .sudo()
                .search_read(
                    [("partner_id", "=", partner.id)],
                    ["name", "merchant_rating", "sequence"],
                )
            )
            for banner in banners:
                banner["banner_image"] = url_join(
                    web_base_url,
                    f'/go/api/image/{banner["id"]}/image_1920/merchant.banner',
                )
            return banners
        except Exception as e:
            return []

    def _get_offer_products(self, partner):
        fields = [
            "name",
            "image_url",
            "list_price",
            "arabic_name",
            "discount",
            "point",
            "offer_label",
            "default_code",
            "barcode",
            "description",
            "description_sale",
            "start_date",
            "end_date",
            "min_quantity",
            "max_quantity",
            "offer_type",
            "offer_type_discount",
            "offer_type_promo_code",
            "merchant_online_store",
            "buy_link",
        ]

        return (
            request.env["product.template"]
            .sudo()
            .search_read(
                [("merchant_id", "=", partner.id), ("is_in_offer", "=", True)], fields
            )
        )

    @http.route(
        [
            "/go/api/user/archive",
            "/go/api/user/account/delete",
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

    @http.route(
        "/go/api/user/location/create",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def create_user_location(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = [
                "customer_id",
                "location_name",
                "zone",
                "building_number",
                "street_number",
            ]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {"error": _("%s Missing") % ", ".join(missing_fields)}

            customer = (
                request.env["res.partner"].sudo().browse(int(data["customer_id"]))
            )
            if not customer.exists():
                return {"error": _("Customer not found in the system")}

            vals = {
                "customer_id": customer.id,
                "location_name": data.get("location_name"),
                "location_landmark": data.get("location_landmark"),
                "zone": data.get("zone"),
                "building_number": data.get("building_number"),
                "street_number": data.get("street_number"),
                "apartment_number": data.get("apartment_number"),
                "floor": data.get("floor"),
                "lat": data.get("lat"),
                "long": data.get("long"),
            }

            address = request.env["user.address"].sudo().create(vals)
            return {
                "success": _("Address created successfully!"),
                "address_id": address.id,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/voucher/code/search",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_user_voucher_code_search(self, **post):
        try:
            data = post or request.env["ir.http"]._get_json_request()
            if "error" in data:
                return data

            current_user = request.env["ir.http"]._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = ["customer_id", "voucher_code"]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {"error": _("%s Missing") % ", ".join(missing_fields)}

            customer = (
                request.env["res.partner"].sudo().browse(int(data["customer_id"]))
            )
            if not customer.exists():
                return {"error": _("Customer not found in the system")}

            valid_voucher_code = "GETVALUESJC15"
            if data.get("voucher_code") != valid_voucher_code:
                return {"error": _("Invalid Voucher Code")}

            return [
                {
                    "voucher_code": valid_voucher_code,
                    "voucher_value": 15,
                    "customer_name": customer.name,
                    "customer_id": customer.id,
                }
            ]
        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/restaurant/create/order",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def create_user_restaurant_order(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = [
                "customer_id",
                "customer_phone",
                "customer_address_id",
                "merchant_id",
                "voucher_applied",
                "delivery_type",
                "order_line",
            ]
            missing_fields = [f for f in required_fields if not data.get(f)]
            if missing_fields:
                return {"error": _("%s Missing") % ", ".join(missing_fields)}

            try:
                order_lines = (
                    data["order_line"]
                    if isinstance(data["order_line"], list)
                    else ast.literal_eval(data["order_line"])
                )
            except Exception:
                return {"error": _("Invalid order_line format")}

            vals = {
                "partner_id": data.get("customer_id"),
                "merchant_id": data.get("merchant_id"),
                "customer_address_id": data.get("customer_address_id"),
                "customer_phone": data.get("customer_phone"),
                "voucher_applied": data.get("voucher_applied"),
                "voucher_value": data.get("voucher_value"),
                "delivery_type": data.get("delivery_type"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": line["product_id"],
                            "name": line["product_id"],
                            "product_uom_qty": line["quantity"],
                            "price_unit": line["price"],
                        },
                    )
                    for line in order_lines
                ],
            }

            order = request.env["loyalty.restaurant.order"].sudo().create(vals)
            return {
                "success": True,
                "message": _("Order created successfully"),
                "id": order.id,
                "name": order.name,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/user/api/user/restro/order/list",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_user_restro_order_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = []
            if data.get("customer_id"):
                domain.append(("partner_id", "=", data["customer_id"]))
            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data["merchant_id"]))
            if data.get("order_id"):
                domain.append(("id", "=", data["order_id"]))

            orders = request.env["loyalty.restaurant.order"].sudo().search(domain)
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            result = []

            for order in orders:
                result.append(
                    {
                        "customer": order.partner_id.name,
                        "customer_id": order.partner_id.id,
                        "order_id": order.id,
                        "order_reference": order.name,
                        "order_status": order.state,
                        "order_create_date": order.create_date,
                        "merchant_id": order.merchant_id.id,
                        "merchant_name": order.merchant_id.name,
                        "merchant_logo": (
                            url_join(
                                web_base_url,
                                f"/go/api/image/{order.merchant_id.id}/image_1920/res.partner",
                            )
                            if order.merchant_id
                            else False
                        ),
                        "delivery_type": order.delivery_type,
                        "customer_phone": order.customer_phone,
                        "customer_address_id": (
                            order.customer_address_id.id
                            if order.customer_address_id
                            else None
                        ),
                        "voucher_applied": order.voucher_applied,
                        "voucher_value": order.voucher_value,
                        "lines": [
                            {
                                "product_id": line.product_id.id,
                                "product_name": line.product_id.name,
                                "quantity": line.product_uom_qty,
                                "price": line.price_unit,
                                "price_subtotal": line.price_subtotal,
                            }
                            for line in order.line_ids
                        ],
                    }
                )
            return result

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/restaurant/order/payment/start",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def restaurant_order_payment_start(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            if not data.get("order_id"):
                return {"error": _("Order ID Missing")}

            pay_url_base = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("go_loyalty.payment_url")
            )
            if not pay_url_base:
                return {"error": _("Payment URL is not configured in system settings")}

            res = [{"order_id": data.get("order_id"), "payUrl": pay_url_base}]

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/terms-conditions",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_terms_conditions(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            app_id = current_user.parent_id.id
            domain = [("organisation_id", "in", [app_id])]

            if data.get("merchant_id"):
                domain.append(("res_partner_id", "=", data.get("merchant_id")))

            terms_matrix = request.env["terms.matrix"].sudo().search(domain, limit=1)
            if not terms_matrix:
                return {
                    "error": _("No Terms and Conditions found for the given criteria.")
                }

            res = [
                {
                    "merchant_id": terms_matrix.res_partner_id.id,
                    "terms_condition": terms_matrix.terms_condition,
                    "terms_condition_ar": terms_matrix.terms_condition_ar,
                    "organisation_id": [org.id for org in terms_matrix.organisation_id],
                }
            ]

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/contracts",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_contract_matrix(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            app_id = current_user.parent_id.id
            domain = [("organisation_id", "in", [app_id])]

            if data.get("merchant_id"):
                domain.append(("res_partner_id", "=", data.get("merchant_id")))

            contract_matrix = (
                request.env["contract.matrix"].sudo().search(domain, limit=1)
            )
            if not contract_matrix:
                return {"error": _("No Contract found for the given criteria.")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            res = [
                {
                    "merchant_id": contract_matrix.res_partner_id.id,
                    "contract_file_url": url_join(
                        web_base_url,
                        f"/web/binary/matrix_contract_download_pdf/{contract_matrix.id}",
                    ),
                    "organisation_id": [
                        org.id for org in contract_matrix.organisation_id
                    ],
                }
            ]

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/merchant/count/premium",
        auth="public",
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_premium_merchant_count(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            # Fetch app IDs linked to the user's parent
            apps = (
                request.env["notin.app"]
                .sudo()
                .search([("parent_id", "=", current_user.parent_id.id)])
            )
            app_ids = apps.ids

            domain = [
                ("is_premium_merchant", "=", True),
                ("active", "=", True),
                ("not_linked_ids", "not in", app_ids),
                ("not_in_list", "=", False),
            ]

            total_count = request.env["res.partner"].sudo().search_count(domain)

            return {"total_premium_merchants": total_count}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/merchant/count/gpoint",
        auth="public",
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_gpoint_merchant_count(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            apps = (
                request.env["notin.app"]
                .sudo()
                .search([("parent_id", "=", current_user.parent_id.id)])
            )
            app_ids = apps.ids

            domain = [
                ("is_premium_merchant", "=", True),
                ("active", "=", True),
                ("not_linked_ids", "not in", app_ids),
                ("not_in_list", "=", False),
            ]

            total_count = request.env["res.partner"].sudo().search_count(domain)

            return {"total_gpoint_merchants": total_count}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/offers-discount-tag",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def get_user_offer_discount_tag(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            app_id = current_user.parent_id.id
            domain = [("organisation_id", "in", [app_id])]

            if data.get("x_for_employee_type"):
                domain += [
                    "|",
                    ("employee_type", "=", data["x_for_employee_type"]),
                    ("employee_type", "=", "both"),
                ]

            if data.get("merchant_id"):
                domain.append(("res_partner_id", "=", data["merchant_id"]))

            merchant_matrix = (
                request.env["merchant.matrix"].sudo().search(domain, limit=1)
            )

            if not merchant_matrix:
                return {
                    "error": _(
                        "No offers or discount tags found for the given criteria."
                    )
                }

            res = []
            for matrix in merchant_matrix:
                res.append(
                    {
                        "merchant_id": matrix.res_partner_id.id,
                        "ribbon_text": matrix.discount_tag,
                        "x_discount_tag_arabic": matrix.discount_tag_arabic,
                        "ribbon_color": matrix.offer_details,
                        "organisation_id": [org.id for org in matrix.organisation_id],
                    }
                )

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/verify/email",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def go_user_verify_email(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            if not partner:
                return {"error": _("No Partner Found for User")}

            partner.sudo().write({"email_verified": True})
            return {"success": _("Email Verified Successfully")}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/dashboard/data",
        type="json",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def go_user_dashboard(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            main_member = not bool(partner.family_head_member_id)
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            limit = int(data.get("limit") or 100)
            offset = int(data.get("offset") or 0)
            banners = (
                request.env["merchant.banner"]
                .sudo()
                .search_read(
                    [
                        ("partner_id.merchant_type", "=", "premium"),
                        ("partner_id.entity_type", "=", "merchant"),
                    ],
                    ["partner_id", "sequence", "merchant_rating"],
                    limit=limit,
                    offset=offset,
                )
            )

            partner_env = request.env["res.partner"].sudo()
            for banner in banners:
                partner_id = banner["partner_id"][0]
                partner_rec = partner_env.browse(partner_id)
                banner.update(
                    {
                        "merchant_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner_id}/image_1920/res.partner",
                        ),
                        "banner_image": url_join(
                            web_base_url,
                            f"/go/api/image/{banner['id']}/image_1920/merchant.banner",
                        ),
                        "ribbon_text": partner_rec.ribbon_text or "",
                        "ribbon_position": partner_rec.ribbon_position or "",
                        "ribbon_color": partner_rec.ribbon_color or "",
                    }
                )

            res = {
                "x_user_expiry": current_user.user_expiry,
                "x_moi_last_name": current_user.moi_last_name,
                "x_first_name_arbic": current_user.first_name_arbic,
                "x_last_name_arbic": current_user.last_name_arbic,
                "main_member": main_member,
                "profile": self._get_partner_profile(partner, web_base_url),
                "premium_merchants": self._get_premium_merchant(web_base_url),
                "standard_merchant": self._get_standard_merchant(web_base_url),
                "merchant_category": self._get_partner_category(web_base_url),
                "members": self._get_family_members(partner),
                "banners": banners,
            }

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    def _get_partner_profile(self, partner, web_base_url):
        return {
            "name": partner.name,
            "create_date": partner.create_date,
            "phone": partner.phone,
            "partner_id": partner.id,
            "email": partner.email,
            "barcode": partner.barcode,
            "address": partner.contact_address,
            "employee_type": partner.employee_type,
            "organisation": partner.parent_id.name,
            "organisation_logo": (
                url_join(
                    web_base_url,
                    f"/go/api/image/{partner.parent_id.id}/image_512/res.partner",
                )
                if partner.parent_id
                else None
            ),
            "photo": url_join(
                web_base_url,
                f"/go/api/image/{partner.id}/image_512/res.partner",
            ),
            "available_points": partner.points,
            "total_points_earn": partner.points_earn,
            "total_points_used": partner.points_used,
            "total_saving": partner.points_values,
            "whatsapp_enabled": partner.enable_whatsapp,
            "whatsapp_title": partner.whatsapp_title,
            "whatsapp_number": partner.whatsapp_number,
            "phoneVerified": partner.phone_verified,
            "emailVerified": partner.email_verified,
            "whatsapp_prefill_message": partner.whatsapp_prefill_message,
        }

    def _get_premium_merchant(self, web_base_url):
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search_read(
                [
                    ("merchant_type", "=", "premium"),
                    ("premium_client", "=", True),
                    ("active", "=", True),
                ],
                [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "partner_latitude",
                    "partner_longitude",
                    "merchant_rating",
                    "partner_category_id",
                ],
            )
        )
        for merchant in merchants:
            merchant["image_512"] = url_join(
                web_base_url,
                f"/go/api/image/{merchant['id']}/image_512/res.partner",
            )
        return merchants

    def _get_standard_merchant(self, web_base_url):
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search_read(
                [
                    ("entity_type", "=", "merchant"),
                    ("merchant_type", "=", "standard"),
                    ("active", "=", True),
                ],
                [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "partner_latitude",
                    "partner_longitude",
                    "merchant_rating",
                    "partner_category_id",
                ],
            )
        )
        for merchant in merchants:
            merchant["image_512"] = url_join(
                web_base_url,
                f"/go/api/image/{merchant['id']}/image_512/res.partner",
            )
        return merchants

    def _get_partner_category(self, web_base_url):
        categories = (
            request.env["partner.category"]
            .sudo()
            .search_read([], ["id", "name", "name_arabic"])
        )
        for category in categories:
            category["image_icon"] = url_join(
                web_base_url,
                f"/go/api/image/{category['id']}/image_icon/partner.category",
            )
        return categories

    def _get_family_members(self, partner):
        return [
            {"name": member.name, "phone": member.phone}
            for member in partner.family_member_ids
        ]

    @http.route(
        "/go/api/user/dashboard/banner",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_user_dashboard_banner(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            banners = (
                request.env["merchant.banner"]
                .sudo()
                .search_read(
                    [
                        ("partner_id.merchant_type", "=", "premium"),
                        ("partner_id.entity_type", "=", "merchant"),
                    ],
                    ["partner_id", "sequence", "merchant_rating"],
                    limit=data.get("limit") or 100,
                    offset=data.get("offset") or 0,
                )
            )

            Partner = request.env["res.partner"].sudo()
            for banner in banners:
                partner = Partner.browse(banner["partner_id"][0])
                banner["merchant_logo"] = url_join(
                    web_base_url, f"/go/api/image/{partner.id}/image_1920/res.partner"
                )
                banner["banner_image"] = url_join(
                    web_base_url,
                    f"/go/api/image/{banner['id']}/image_1920/merchant.banner",
                )
                banner["ribbon_text"] = partner.ribbon_text
                banner["ribbon_position"] = partner.ribbon_position
                banner["ribbon_color"] = partner.ribbon_color

            return banners

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        "/go/api/user/merchant/banner",
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def go_user_dashboard_banner(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            merchant_id = data.get("merchant_id")
            if not merchant_id:
                return {"error": _("Provide Merchant ID")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            banners = (
                request.env["merchant.banner"]
                .sudo()
                .search_read(
                    [
                        ("partner_id.merchant_type", "=", "premium"),
                        ("partner_id.entity_type", "=", "merchant"),
                        ("partner_id.id", "=", int(merchant_id)),
                    ],
                    ["id", "partner_id", "sequence", "merchant_rating"],
                    limit=int(data.get("limit") or 100),
                    offset=int(data.get("offset") or 0),
                )
            )

            for banner in banners:
                partner_id = banner["partner_id"][0]
                partner = request.env["res.partner"].sudo().browse(partner_id)

                banner.update(
                    {
                        "merchant_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner_id}/image_1920/res.partner",
                        ),
                        "banner_image": url_join(
                            web_base_url,
                            f'/go/api/image/{banner["id"]}/image_1920/merchant.banner',
                        ),
                        "ribbon_text": partner.ribbon_text or "",
                        "ribbon_position": partner.ribbon_position or "",
                        "ribbon_color": partner.ribbon_color or "",
                    }
                )

            return banners

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        "/go/api/user/sales/transaction/data",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def go_user_sales_transaction_data(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id

            transactions = (
                request.env["loyalty.sale"]
                .sudo()
                .search([("partner_id", "=", partner.id)])
            )
            transaction_lines = transactions.mapped("transaction_ids").filtered(
                lambda l: l.partner_id.id == partner.id
            )

            sales_by_category = (
                request.env["loyalty.sale"]
                .sudo()
                .read_group(
                    [("partner_id", "=", partner.id)],
                    ["merchant_category_id", "discount", "amount", "points"],
                    ["merchant_category_id"],
                )
            )

            sales_by_merchant = (
                request.env["loyalty.sale"]
                .sudo()
                .read_group(
                    [("partner_id", "=", partner.id)],
                    ["merchant_id", "discount", "amount", "points"],
                    ["merchant_id"],
                )
            )

            Category = request.env["partner.category"].sudo()
            Partner = request.env["res.partner"].sudo()

            transactions_by_category = [
                {
                    "category": Category.browse(data["merchant_category_id"][0]).name,
                    "merchant_category_id": data["merchant_category_id"][0],
                    "merchant_category_logo": Category.browse(
                        data["merchant_category_id"][0]
                    ).image_icon,
                    "discount": data["discount"],
                    "sales": data["amount"],
                    "points": data["points"],
                }
                for data in sales_by_category
            ]

            transactions_by_merchant = [
                {
                    "merchant_name": Partner.browse(data["merchant_id"][0]).name,
                    "merchant_id": data["merchant_id"][0],
                    "merchant_logo": Partner.browse(data["merchant_id"][0]).image_1920,
                    "category_id": Partner.browse(
                        data["merchant_id"][0]
                    ).partner_category_id.id,
                    "discount": data["discount"],
                    "sales": data["amount"],
                    "points": data["points"],
                }
                for data in sales_by_merchant
            ]

            result = {
                "available_points": partner.points,
                "total_saving": sum(transactions.mapped("discount")),
                "points_used": sum(transaction_lines.mapped("debit")),
                "points_earned": sum(transaction_lines.mapped("credit")),
                "transactions_by_category": transactions_by_category,
                "transactions_by_merchant": transactions_by_merchant,
            }

            return result

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/user/merchant/moi/details"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_user_merchant_moi_details(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            merchant_id = data.get("merchant_id")
            if not merchant_id:
                return {"error": _("Merchant ID Missing")}

            merchant = request.env["res.partner"].sudo().browse(int(merchant_id))
            if merchant.entity_type != "merchant":
                return {"error": _("Provided merchant is not registered with us")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            return self._get_user_merchant_moi_profile(merchant, web_base_url)

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    def _get_user_merchant_moi_profile(self, partner, web_base_url):
        products = self._get_products(partner)
        category = partner.partner_category_id

        return {
            "merchant_name": partner.name,
            "x_for_employee_type": partner.employee_type,
            "x_arabic_name": partner.arabic_name,
            "phone": partner.phone,
            "email": partner.email,
            "website": partner.website,
            "merchant_code": partner.barcode,
            "open_from": partner.open_from,
            "open_till": partner.open_till,
            "address": partner.contact_address,
            "partner_latitude": partner.partner_latitude,
            "partner_longitude": partner.partner_longitude,
            "ribbon_text": partner.ribbon_text,
            "ribbon_color": partner.ribbon_color,
            "ribbon_position": partner.ribbon_position,
            "description": partner.merchant_details_moi_en,
            "description_arabic": partner.merchant_details_moi_ar,
            "x_online_store": partner.online_store,
            "rating": partner.merchant_rating,
            "notes": partner.comment,
            "map_banner": url_join(
                web_base_url, f"/go/api/image/{partner.id}/map_banner/res.partner"
            ),
            "merchant_logo": url_join(
                web_base_url, f"/go/api/image/{partner.id}/image_512/res.partner"
            ),
            "category": category.name,
            "category_logo": url_join(
                web_base_url, f"/go/api/image/{category.id}/image_icon/partner.category"
            ),
            "banners": self._get_banners(partner, web_base_url),
            "products": products,
            "is_hotel": partner.is_hotel_type,
            "x_kts": partner.kts,
            "offer_products": self._get_offer_products(partner),
            "whatsapp_enabled": partner.enable_whatsapp,
            "whatsapp_title": partner.whatsapp_title,
            "whatsapp_number": partner.whatsapp_number,
            "whatsappx_prefill_message": partner.whatsapp_prefill_message,
            "pdf_attached": partner.pdf_attached,
            "company_contract_url": url_join(
                web_base_url, f"/web/binary/contract_download_pdf/{partner.id}"
            ),
            "company_registartion_url": url_join(
                web_base_url, f"/web/binary/registration_download_pdf/{partner.id}"
            ),
            "x_terms_condition": partner.terms_condition,
            "x_terms_condition_arabic": partner.terms_condition_arabic,
            "x_terms_condition_new": partner.terms_conditions_en,
            "x_terms_condition_arabic_new": partner.terms_conditions_ar,
            "x_moi_show": partner.show_in_moi,
            "x_contact_number_ar": partner.ar_contact_number,
            "x_email_ar": partner.ar_email,
            "x_street_ar": partner.ar_street,
            "x_city_ar": partner.ar_city,
            "x_country_ar": partner.ar_country,
            "x_time_from_ar": partner.ar_time_from,
            "x_time_to_ar": partner.ar_time_to,
        }

    def _get_products(self, partner):
        return (
            request.env["product.template"]
            .sudo()
            .search_read(
                [("merchant_id", "=", partner.id), ("is_in_offer", "=", False)],
                [
                    "name",
                    "image_url",
                    "list_price",
                    "arabic_name",
                    "discount",
                    "point",
                    "offer_label",
                    "default_code",
                    "barcode",
                    "description",
                    "description_sale",
                ],
            )
        )

    @http.route(
        ["/go/api/user/merchant/child/lists"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_user_merchant_child_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            domain = [("entity_type", "=", "merchant"), ("active", "=", True)]
            if data.get("parent_id"):
                domain.append(("parent_id", "=", int(data["parent_id"])))

            limit = int(data.get("limit", 0)) if data.get("limit") else 0
            offset = int(data.get("offset", 0))
            merchants_env = request.env["res.partner"].sudo()

            if limit:
                merchants = merchants_env.search(
                    domain, order="sequence", offset=offset, limit=limit
                )
            else:
                merchants = merchants_env.search(domain, order="sequence")

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            Notification = request.env["loyalty.notification"].sudo()
            res = []

            for partner in merchants:
                notification = Notification.search(
                    [("merchant_id", "=", partner.id)], limit=1
                )
                res.append(
                    {
                        "merchant_name": partner.name,
                        "x_for_employee_type": partner.employee_type,
                        "is_business_hotel": partner.is_hotel_type,
                        "x_kts": partner.kts,
                        "merchant_id": partner.id,
                        "x_online_store": partner.online_store,
                        "x_sequence": partner.sequence,
                        "barcode": partner.barcode,
                        "partner_latitude": partner.partner_latitude,
                        "partner_longitude": partner.partner_longitude,
                        "ribbon_text": partner.ribbon_text,
                        "ribbon_color": partner.ribbon_color,
                        "ribbon_position": partner.ribbon_position,
                        "rating": partner.merchant_rating,
                        "map_banner": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/map_banner/res.partner",
                        ),
                        "merchant_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/image_512/res.partner",
                        ),
                        "category": partner.partner_category_id.name,
                        "category_id": partner.partner_category_id.id,
                        "category_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
                        ),
                        "country_id": partner.country_id.id,
                        "country_name": partner.country_id.name,
                        "banners": self._get_banners(partner, web_base_url),
                        "pdf_attached": partner.pdf_attached,
                        "company_contract_url": url_join(
                            web_base_url,
                            f"/web/binary/contract_download_pdf/{partner.id}",
                        ),
                        "company_registartion_url": url_join(
                            web_base_url,
                            f"/web/binary/registration_download_pdf/{partner.id}",
                        ),
                    }
                )

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/user/restaurant/category/lists"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_user_restaurant_category_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            categories = self._get_partner_category_restro(web_base_url)

            return {"restro_category": categories}

        except Exception as e:
            return {"error": str(e)}

    def _get_partner_category_restro(self, web_base_url):
        categories = (
            request.env["loyalty.restaurant.category"]
            .sudo()
            .search_read([], ["id", "name", "parent_id", "name_arabic"])
        )
        return categories

    @http.route(
        ["/go/api/user/location/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_location_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = []
            if data.get("customer_id"):
                domain.append(("customer_id", "=", data["customer_id"]))

            addresses = request.env["user.address"].sudo().search(domain)
            res = []

            for addr in addresses:
                res.append(
                    {
                        "customer": addr.customer_id.name,
                        "customer_id": addr.customer_id.id,
                        "location_id": addr.id,
                        "street_number": addr.street_number,
                        "location_name": addr.location_name,
                        "building_number": addr.building_number,
                        "zone": addr.zone,
                        "floor": addr.floor,
                        "apartment_number": addr.apartment_number,
                        "latitude": addr.lat,
                        "longitude": addr.long,
                    }
                )

            return res

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        "/go/api/user/validate",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def validate_user(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            email = data.get("email")
            phone = data.get("phone")
            validate_code = data.get("validate_code")
            method = data.get("method")

            if not validate_code or not method:
                return {
                    "status": "error",
                    "message": _("The fields validate_code and method are mandatory."),
                }

            if not email and not phone:
                return {
                    "status": "error",
                    "message": _("Either email or phone is required."),
                }

            if method == "email":
                if not email:
                    return {
                        "status": "error",
                        "message": _("Email is required for the email method."),
                    }

                email_body = f"""
                        <html>
                        <body>
                            <p>Dear User,</p>
                            <p>Thanks for using our Application!</p>
                            <p>Kindly use the below confirmation code to validate your email:</p>
                            <p style="font-size:18px;font-weight:bold;color:#2b7dfa;">{validate_code}</p>
                            <p>Best Regards,<br>Support Team</p>
                        </body>
                        </html>
                    """

                vals = {
                    "subject": "Thanks for using Golalita",
                    "body_html": email_body,
                    "email_to": email,
                    "auto_delete": False,
                    "email_from": "support@golalita.com",
                }

                request.env["mail.mail"].sudo().create(vals).sudo().send()
            elif method == "phone":
                if not phone:
                    return {
                        "status": "error",
                        "message": _("Phone is required for the phone method."),
                    }
            else:
                return {
                    "status": "error",
                    "message": _("Invalid method. Accepted values are email or phone."),
                }

            return {"status": "success", "message": _("Validation successful.")}

        except Exception as e:
            return {
                "status": "error",
                "message": _("An unexpected error occurred: %s") % str(e),
            }

    # Todo
    @http.route(
        ["/go/api/user/moi/remove/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def send_moi_mail_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            auth_header = request.httprequest.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"error": _("Unauthorized: Bearer token missing or invalid")}

            token = auth_header.split(" ")[1]
            if token != BEARER_TOKEN:
                return {"error": _("Unauthorized: Invalid Bearer token")}

            customer_name = data.get("customer_name")
            customer_email = data.get("customer_email")
            customer_phone = data.get("customer_phone")

            if not customer_email and not customer_phone:
                return {"error": _("Email or Phone No. Missing")}

            domain = []
            if customer_email and customer_phone:
                domain = [
                    "|",
                    ("email", "=", customer_email),
                    ("phone", "=", customer_phone),
                ]
            elif customer_email:
                domain = [("email", "=", customer_email)]
            elif customer_phone:
                domain = [("phone", "=", customer_phone)]

            partner = request.env["res.partner"].sudo().search(domain, limit=1)

            is_registered = bool(partner)
            org_type = (
                dict(partner._fields["org_type"].selection).get(partner.org_type)
                if partner
                else "Not Registered"
            )

            email_body = f"""
                    <p>Dear Support Team,</p>
                    <p>The customer has requested data deletion via MOI:</p>
                    <ul>
                        <li><strong>Name:</strong> {customer_name or 'Not Provided'}</li>
                        <li><strong>Email:</strong> {customer_email or 'Not Provided'}</li>
                        <li><strong>Phone:</strong> {customer_phone or 'Not Provided'}</li>
                    </ul>
                    <p>Regards,</p>
                    <p><strong>Golalita API</strong></p>
                    """

            vals = {
                "subject": "Customer Information Delete Request - MOI - Golalita",
                "body_html": email_body,
                "email_to": "abhishek.ricky88@gmail.com",
                "email_cc": "info@golalita.com",
                "auto_delete": False,
                "email_from": "support@golalita.com",
            }

            mail = request.env["mail.mail"].sudo().create(vals)
            mail.sudo().send()

            return {
                "success": _(
                    "Delete request submitted successfully. Expect confirmation within 3 hours."
                ),
                "is_registered": is_registered,
                "org_type": org_type,
            }

        except Exception as e:
            return {"error": _("Unexpected error: %s") % str(e)}

    @http.route(
        ["/go/api/user/offers/golalita/v3"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_users_offer_list_golalita_v3(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [
                ("merchant_id", "!=", False),
                ("is_in_offer", "=", True),
                ("home_offer", "=", True),
                ("offer_type", "!=", "b1g1"),
            ]

            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data.get("merchant_id")))

            if data.get("merchant_category_id"):
                merchants = (
                    request.env["res.partner"]
                    .sudo()
                    .search(
                        [("partner_category_id", "=", data.get("merchant_category_id"))]
                    )
                )
                domain.append(("merchant_id", "in", merchants.ids))

            if data.get("x_offer_type"):
                domain.append(("offer_type", "=", data.get("x_offer_type")))

            if data.get("subscribed_merchant_offer"):
                lines = (
                    request.env["loyalty.notification.line"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", current_user.partner_id.id),
                            ("is_subscribe", "=", True),
                        ]
                    )
                )
                merchant_ids = lines.mapped("notification_id.merchant_id").ids
                if merchant_ids:
                    domain.append(("merchant_id", "in", merchant_ids))

            fields = [
                "name",
                "arabic_name",
                "image_url",
                "list_price",
                "default_code",
                "point",
                "online_store",
                "max_quantity",
                "offer_type",
                "offer_type_discount",
                "offer_type_promo_code",
                "merchant_online_store",
                "buy_link",
                "barcode",
                "description",
                "description_sale",
                "description_arabic",
                "offer_label",
                "label_arabic",
                "merchant_id",
                "categ_id",
                "create_date",
                "start_date",
                "end_date",
                "min_quantity",
                "discount",
            ]

            products = (
                request.env["product.template"]
                .sudo()
                .search_read(
                    domain,
                    fields,
                    limit=data.get("limit", 100000),
                    offset=data.get("offset", 0),
                )
            )

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            datas = []

            for product in products:
                product_template = (
                    request.env["product.template"].sudo().browse(product["id"])
                )
                merchant = product_template.merchant_id

                product["ribbon"] = ""
                product["merchant_name"] = merchant.name
                product["merchant_id"] = merchant.id
                product["merchant_name_arabic"] = merchant.arabic_name
                product["phone_number"] = merchant.phone
                product["mobile_number"] = merchant.mobile
                product["merchant_email"] = merchant.email
                product["merchant_rating"] = 4
                product["category_id"] = (
                    product["categ_id"][0] if product["categ_id"] else False
                )
                product["category_name"] = (
                    product["categ_id"][1] if product["categ_id"] else ""
                )
                product["disc_ribbon"] = product["offer_label"]
                product["point"] = product["point"]
                product["product_merchant_is_business_hotel"] = merchant.id
                product["merchant_logo"] = url_join(
                    web_base_url, f"/go/api/image/{merchant.id}/image_1920/res.partner"
                )

                datas.append(product)

            return datas

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        ["/go/api/user/merchant/lists/premium"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_user_category_merchant_premium_list(self, **post):

        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        app_ids = (
            request.env["notin.app"]
            .sudo()
            .search_read([("parent_id", "=", current_user.parent_id.id)], ["id"])
        )
        app_id_list = [a["id"] for a in app_ids]

        domain = [
            ("entity_type", "=", "merchant"),
            ("is_premium_merchant", "=", True),
            ("not_linked_ids", "not in", app_id_list),
            ("not_in_list", "=", False),
        ]

        field_mapping = {
            "category_id": ("partner_category_id", "child_of"),
            "gpoint": ("go_loyalty_point", "="),
            "country_id": ("country_id", "="),
            "x_online_store": ("online_store", "="),
            "merchant_type": ("merchant_type", "="),
            "merchant_id": ("id", "="),
            "location_id": ("location_id", "="),
        }
        for field, (name, op) in field_mapping.items():
            if data.get(field):
                domain.append((name, op, data[field]))

        # Special filters
        if data.get("x_for_employee_type"):
            emp_type = data["x_for_employee_type"]
            domain += [
                "|",
                ("employee_type", "=", emp_type),
                ("employee_type", "=", "both"),
            ]

        if data.get("x_org_linked"):
            org = data["x_org_linked"]
            domain += ["|", ("org_type", "=", org), ("org_type", "=", None)]

        if data.get("merchant_name"):
            name = data["merchant_name"]
            domain += ["|", ("name", "ilike", name), ("arabic_name", "ilike", name)]

        # Fetch merchants
        offset = int(data.get("offset", 0))
        limit = int(data.get("limit")) if data.get("limit") else None
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search(domain, order="sequence", offset=offset, limit=limit)
        )

        web_base_url = (
            request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        Notification = request.env["loyalty.notification"].sudo()

        res = []
        for partner in merchants:
            notification = Notification.search(
                [("merchant_id", "=", partner.id)], limit=1
            )

            res.append(
                {
                    "merchant_id": partner.id,
                    "merchant_name": partner.name,
                    "x_arabic_name": partner.arabic_name,
                    "x_for_employee_type": partner.employee_type,
                    "is_business_hotel": partner.is_hotel_type,
                    "x_moi_show": partner.x_moi_show,
                    "x_have_branch": partner.x_have_branch,
                    "x_have_offers": partner.x_have_offers,
                    "accept_go_loyalty_point": partner.go_loyalty_point,
                    "gpoint": partner.go_loyalty_point,
                    "open_from": partner.open_from,
                    "open_till": partner.open_till,
                    "x_kts": partner.kts,
                    "x_org_linked": partner.org_type,
                    "x_online_store": partner.online_store,
                    "x_sequence": partner.sequence,
                    "barcode": partner.barcode,
                    "email": partner.email,
                    "partner_latitude": partner.partner_latitude,
                    "partner_longitude": partner.partner_longitude,
                    "ribbon_text": partner.ribbon_text,
                    "x_ribbon_text_arabic": partner.ribbon_text_ar,
                    "ribbon_color": partner.ribbon_color,
                    "ribbon_position": partner.ribbon_position,
                    "rating": partner.merchant_rating,
                    "map_banner": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.id}/map_banner/res.partner",
                    ),
                    "merchant_logo": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.id}/image_512/res.partner",
                    ),
                    "category": partner.partner_category_id.name,
                    "category_id": partner.partner_category_id.id,
                    "country_id": partner.country_id.id,
                    "country_code": partner.country_id.code,
                    "country_name": partner.country_id.name,
                    "category_logo": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
                    ),
                    "banners": self._get_banners(partner, web_base_url),
                    "pdf_attached": partner.pdf_attached,
                    "company_contract_url": url_join(
                        web_base_url, f"/web/binary/contract_download_pdf/{partner.id}"
                    ),
                    "company_registration_url": url_join(
                        web_base_url,
                        f"/web/binary/registration_download_pdf/{partner.id}",
                    ),
                }
            )

        return res

    @http.route(
        ["/go/api/user/offer/details"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_user_offer_details(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = (
                request.env["res.users"]
                .sudo()
                .search([("token", "=", data.get("token"))])
            )
            if not current_user:
                return {"error": _("Invalid User Token")}

            product_id = data.get("product_id")
            if not product_id:
                return {"error": _("Product ID is required")}

            product = (
                request.env["product.template"]
                .sudo()
                .search([("id", "=", product_id)], limit=1)
            )
            if not product:
                return {"error": _("Product not found")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            merchant_contract_url = (
                url_join(
                    web_base_url,
                    f"/web/binary/contract_download_pdf/{product.merchant_id.id}",
                )
                if product.merchant_id and product.merchant_id.contract_copy
                else False
            )
            offer_detail_url = (
                url_join(web_base_url, f"/web/binary/offer_download_pdf/{product.id}")
                if product.offer_copy
                else False
            )

            product_branches = (
                [
                    {
                        "merchant_id": branch.id,
                        "merchant_name": branch.name,
                        "merchant_name_ar": branch.arabic_name,
                        "merchant_logo": (
                            url_join(
                                web_base_url,
                                f"/go/api/image/{branch.id}/image_1920/res.partner",
                            )
                            if branch
                            else False
                        ),
                        "location_name": (
                            branch.location_id.name if branch.location_id else False
                        ),
                    }
                    for branch in product.branch_ids.sudo()
                ]
                if product.branch_ids
                else []
            )

            product_details = {
                "product_id": product.id,
                "name": product.name,
                "arabic_name": product.arabic_name,
                "image_url": product.image_url,
                "price": product.list_price,
                "default_code": product.default_code,
                "points": product.point,
                "online_store": product.online_store,
                "max_quantity": product.max_quantity,
                "offer_type": product.offer_type,
                "offer_type_discount": product.offer_type_discount,
                "offer_type_promo_code": product.offer_type_promo_code,
                "merchant_id": product.merchant_id.id if product.merchant_id else False,
                "merchant_name": (
                    product.merchant_id.name if product.merchant_id else False
                ),
                "merchant_name_arabic": (
                    product.merchant_id.arabic_name if product.merchant_id else False
                ),
                "merchant_phone": (
                    product.merchant_id.phone if product.merchant_id else False
                ),
                "merchant_mobile": (
                    product.merchant_id.mobile if product.merchant_id else False
                ),
                "merchant_email": (
                    product.merchant_id.email if product.merchant_id else False
                ),
                "category_id": product.categ_id.id if product.categ_id else False,
                "category_name": product.categ_id.name if product.categ_id else False,
                "description": product.description,
                "description_sale": product.description_sale,
                "description_arabic": product.description_arabic,
                "offer_label": product.offer_label,
                "label_arabic": product.label_arabic,
                "merchant_logo": (
                    url_join(
                        web_base_url,
                        f"/go/api/image/{product.merchant_id.id}/image_1920/res.partner",
                    )
                    if product.merchant_id
                    else False
                ),
                "barcode": product.barcode,
                "start_date": product.start_date,
                "end_date": product.end_date,
                "min_quantity": product.min_quantity,
                "discount": product.discount,
                "merchant_contract_url": merchant_contract_url,
                "offer_detail_url": offer_detail_url,
                "branches": product_branches,
            }

            return product_details

        except Exception as e:
            return {"error": _("Unexpected error: %s") % str(e)}

    # @http.route(
    #     ["/go/api/user/scan/bills"],
    #     type="json",
    #     auth="public",
    #     methods=["POST"],
    #     csrf=False,
    # )
    # def scan_bills(self, **post):
    #     try:
    #         data = post or self._get_json_request()
    #         if "error" in data:
    #             return data
    #
    #         current_user = self._validate_token(data)
    #         if isinstance(current_user, dict):
    #             return current_user
    #
    #         required_params = [
    #             "customer_name",
    #             "customer_id",
    #             "customer_phone",
    #             "customer_email",
    #             "total_bill_amount",
    #             "merchant_name",
    #             "geo_latitude",
    #             "geo_longitude",
    #             "date",
    #             "time",
    #         ]
    #
    #         missing_params = [param for param in required_params if not data.get(param)]
    #         if missing_params:
    #             return {
    #                 "status": "error",
    #                 "message": f"Missing required parameters: {', '.join(missing_params)}",
    #             }
    #
    #         try:
    #             total_bill_amount = float(data.get("total_bill_amount"))
    #             geo_latitude = float(data.get("geo_latitude"))
    #             geo_longitude = float(data.get("geo_longitude"))
    #         except ValueError:
    #             return {
    #                 "status": "error",
    #                 "message": _(
    #                     "Invalid numeric values for latitude, longitude, or amount"
    #                 ),
    #             }
    #
    #         return {
    #             "status": "success",
    #             "message": _("Data received successfully."),
    #             "data": {
    #                 "customer_name": data.get("customer_name"),
    #                 "customer_id": data.get("customer_id"),
    #                 "customer_phone": data.get("customer_phone"),
    #                 "customer_email": data.get("customer_email"),
    #                 "total_bill_amount": total_bill_amount,
    #                 "merchant_name": data.get("merchant_name"),
    #                 "geo_latitude": geo_latitude,
    #                 "geo_longitude": geo_longitude,
    #                 "date": data.get("date"),
    #                 "time": data.get("time"),
    #             },
    #         }
    #
    #     except Exception as e:
    #         return {
    #             "status": "error",
    #             "message": _("Unexpected error occurred."),
    #             "details": str(e),
    #         }

    @http.route(
        ["/go/api/user/get/locations"],
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def get_locations(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            locations = request.env["custom.location"].sudo().search([])
            location_data = [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "arabic_name": loc.arabic_name,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                    "short_names": [
                        {
                            "id": short_name.id,
                            "name": short_name.name,
                            "location_id": loc.id,
                        }
                        for short_name in loc.short_name_ids
                    ],
                }
                for loc in locations
            ]

            return {
                "status": "success",
                "data": location_data,
            }

        except Exception as e:
            return {
                "status": "error",
                "message": _("Unexpected error occurred."),
                "details": str(e),
            }

    @http.route(
        [
            "/go/api/user/moi-api-call",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_moi_user_call(self, **post):
        # Get JSON data safely
        data = post or self._get_json_request()
        if "error" in data:
            return data

        activation_code = data.get("activationCode")
        id_card_exp_date = data.get("idCardExpDate")

        if not activation_code:
            return {"error": _("Provide Code")}
        if not id_card_exp_date:
            return {"error": _("Provide Expiry Date")}

        user_name = "testuser"

        # Check if the request matches any sample data
        if (activation_code, id_card_exp_date) == ("6HGHJBZSRJ", "2027-03-06"):
            response_text = """Status Code: 200\n\nResponse Body:\n<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns2:getEmtiyazCardDetailsResponse xmlns:ns2="http://ejb.hrx.moi.gov.qa/"><return><cardNumber>01-0373-111111-00-01</cardNumber><cardType>V</cardType><firstNameAr>علي</firstNameAr><firstNameEn>Ali</firstNameEn><lastNameAr>اليافعي</lastNameAr><lastNameEn>Al Yafei</lastNameEn><responseCode>1</responseCode></return></ns2:getEmtiyazCardDetailsResponse></soapenv:Body></soapenv:Envelope>"""
            return response_text

        elif (activation_code, id_card_exp_date) == ("TESR167187", "2026-01-06"):
            response_text = """Status Code: 200\n\nResponse Body:\n<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns2:getEmtiyazCardDetailsResponse xmlns:ns2="http://ejb.hrx.moi.gov.qa/"><return><cardNumber>01-0373-11617190-00-01</cardNumber><cardType>V</cardType><firstNameAr>علي</firstNameAr><firstNameEn>Ali</firstNameEn><lastNameAr>اليافعي</lastNameAr><lastNameEn>Al Yafei</lastNameEn><responseCode>1</responseCode></return></ns2:getEmtiyazCardDetailsResponse></soapenv:Body></soapenv:Envelope>"""
            return response_text

        elif (activation_code, id_card_exp_date) == ("6HGH156176", "2028-04-01"):
            response_text = """Status Code: 200\n\nResponse Body:\n<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns2:getEmtiyazCardDetailsResponse xmlns:ns2="http://ejb.hrx.moi.gov.qa/"><return><cardNumber>01-0373-8611711-00-01</cardNumber><cardType>V</cardType><firstNameAr>علي</firstNameAr><firstNameEn>Ali</firstNameEn><lastNameAr>اليافعي</lastNameAr><lastNameEn>Al Yafei</lastNameEn><responseCode>1</responseCode></return></ns2:getEmtiyazCardDetailsResponse></soapenv:Body></soapenv:Envelope>"""
            return response_text

        elif (activation_code, id_card_exp_date) == ("KHATGH6171", "2029-02-01"):
            response_text = """Status Code: 200\n\nResponse Body:\n<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns2:getEmtiyazCardDetailsResponse xmlns:ns2="http://ejb.hrx.moi.gov.qa/"><return><cardNumber>01-0373-92134158-00-01</cardNumber><cardType>V</cardType><firstNameAr>علي</firstNameAr><firstNameEn>Ali</firstNameEn><lastNameAr>اليافعي</lastNameAr><lastNameEn>Al Yafei</lastNameEn><responseCode>1</responseCode></return></ns2:getEmtiyazCardDetailsResponse></soapenv:Body></soapenv:Envelope>"""
            return response_text

        elif (activation_code, id_card_exp_date) == ("A1TEST99", "2028-01-01"):
            response_text = """Status Code: 200\n\nResponse Body:\n<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Body><ns2:getEmtiyazCardDetailsResponse xmlns:ns2="http://ejb.hrx.moi.gov.qa/"><return><cardNumber>01-0374-000000-00-01</cardNumber><cardType>V</cardType><firstNameAr>عبدالله</firstNameAr><firstNameEn>Abdulla</firstNameEn><lastNameAr>اليافعي</lastNameAr><lastNameEn>Al Yafei</lastNameEn><responseCode>1</responseCode></return></ns2:getEmtiyazCardDetailsResponse></soapenv:Body></soapenv:Envelope>"""
            return response_text

        url = "https://newgolalitaapim.azure-api.net/emtiyazcard/"

        headers = {
            "Ocp-Apim-Subscription-Key": "4282a5cc63804c528c71a908f03fb7fe",
            "Content-Type": "application/json",
        }

        payload = {
            "activationCode": activation_code,
            "idCardExpDate": id_card_exp_date,
            "userName": user_name,
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_text = (
            f"Status Code: {response.status_code}\n\nResponse Body:\n{response.text}"
        )
        return response_text

    @http.route(
        ["/go/api/user/merchant/lists/app"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_user_merchant_list_app(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        apps = (
            request.env["notin.app"]
            .sudo()
            .search([("parent_id", "=", current_user.parent_id.id)])
        )
        app_ids = apps.mapped("id")

        domain = [
            ("entity_type", "=", "merchant"),
            ("not_linked_ids", "not in", app_ids),
        ]

        filters = {
            "category_id": ("partner_category_id", "child_of"),
            "country_id": ("country_id", "="),
            "merchant_name": ("name", "="),
            "merchant_type": ("merchant_type", "="),
            "merchant_id": ("id", "="),
        }
        for key, (field, operator) in filters.items():
            if data.get(key):
                domain.append((field, operator, data[key]))

        limit = int(data.get("limit", 0)) or None
        offset = int(data.get("offset", 0))
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search(domain, order="sequence", offset=offset, limit=limit)
        )

        web_base_url = (
            request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        Notification = request.env["loyalty.notification"].sudo()

        res = []
        for partner in merchants:
            notification = Notification.search(
                [("merchant_id", "=", partner.id)], limit=1
            )
            res.append(
                {
                    "merchant_name": partner.name,
                    "is_business_hotel": partner.is_hotel_type,
                    "x_moi_show": partner.show_in_moi,
                    "x_kts": partner.kts,
                    "merchant_id": partner.id,
                    "accept_go_loyalty_point": partner.go_loyalty_point,
                    "x_online_store": partner.online_store,
                    "x_sequence": partner.sequence,
                    "barcode": partner.barcode,
                    "partner_latitude": partner.partner_latitude,
                    "partner_longitude": partner.partner_longitude,
                    "ribbon_text": partner.ribbon_text,
                    "ribbon_color": partner.ribbon_color,
                    "ribbon_position": partner.ribbon_position,
                    "rating": partner.merchant_rating,
                    "map_banner": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.id}/map_banner/res.partner",
                    ),
                    "merchant_logo": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.id}/image_512/res.partner",
                    ),
                    "category": partner.partner_category_id.name,
                    "category_id": partner.partner_category_id.id,
                    "country_id": partner.country_id.id,
                    "country_name": partner.country_id.name,
                    "category_logo": url_join(
                        web_base_url,
                        f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
                    ),
                    "banners": self._get_banners(partner, web_base_url),
                    "pdf_attached": partner.pdf_attached,
                    "company_contract_url": url_join(
                        web_base_url, f"/web/binary/contract_download_pdf/{partner.id}"
                    ),
                    "company_registartion_url": url_join(
                        web_base_url,
                        f"/web/binary/registration_download_pdf/{partner.id}",
                    ),
                }
            )

        return res

    @http.route(
        ["/go/api/user/restro/order/detail/id"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_restro_order_detail_id(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        domain = []
        if data.get("customer_id"):
            domain.append(("partner_id", "=", data["customer_id"]))
        if data.get("merchant_id"):
            domain.append(("merchant_id", "=", data["merchant_id"]))
        if data.get("order_id"):
            domain.append(("id", "=", data["order_id"]))

        orders = request.env["loyalty.restaurant.order"].sudo().search(domain)
        web_base_url = (
            request.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )

        res = []
        for order in orders:
            customer_address = order.customer_address_id
            res.append(
                {
                    "merchant_logo": url_join(
                        web_base_url,
                        f"/go/api/image/{order.merchant_id.id}/image_1920/res.partner",
                    ),
                    "merchant_name": order.merchant_id.name,
                    "merchant_phone": order.merchant_id.phone,
                    "delivery_preparation_time": order.merchant_id.time_for_order_prepration,
                    "delivery_type": order.delivery_type,
                    "order_create_date": order.create_date,
                    "order_id": order.id,
                    "order_reference": order.name,
                    "order_status": order.state,
                    "delivery_address": {
                        "short": customer_address.location_name,
                        "long": f"Location {customer_address.location_name} Zone: {customer_address.zone} Street: {customer_address.street_number} Building: {customer_address.building_number}",
                        "zone": customer_address.zone,
                        "street_number": customer_address.street_number,
                        "building_number": customer_address.building_number,
                        "apartment_number": customer_address.apartment_number,
                        "floor": customer_address.floor,
                        "latitude": customer_address.lat,
                        "longitude": customer_address.long,
                    },
                    "products": [
                        {
                            "product_id": line.product_id.id,
                            "product_name": line.product_id.name,
                            "product_description": line.product_id.description,
                            "quantity": line.product_uom_qty,
                            "price": line.price_unit,
                            "discount": line.discount or 0,
                            "price_subtotal": line.price_subtotal,
                        }
                        for line in order.line_ids
                    ],
                    "voucher_discount": order.voucher_value,
                    "delivery_fee": order.merchant_id.delivery_cost,
                    "total_amount": order.amount_total,
                }
            )

        return res

    # TODO: Secure this endpoint properly before production use (Dhiren 2025-10-19)
    @http.route(
        '/go/moi/user/test-verify',
        auth="public",
        methods=['POST'],
        csrf=False,
        type='json',
        cors='*'
    )
    def verify_moi_user(self, **post):
        """Verifies the user using barcode, branch_id, and amount value with secure HMAC authentication."""

        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            barcode_number = data.get('barcode_number')
            branch_id = data.get('branch_id')
            amount_value = data.get('amount_value')
            provided_signature = data.get('signature')

            # Validate required fields
            missing_fields = [f for f in ['barcode_number', 'branch_id', 'amount_value', 'signature'] if not data.get(f)]
            if missing_fields:
                return {'error': f"Missing required parameters: {', '.join(missing_fields)}"}

            if float(amount_value) <= 0:
                return {'error': 'Amount value must be greater than zero'}

            # Generate expected signature
            message = f"{barcode_number}|{branch_id}|{format(float(amount_value), '.2f')}"
            expected_signature = hmac.new(
                SECRET_KEY.encode(), message.encode(), hashlib.sha256
            ).digest()
            expected_signature = base64.b64encode(expected_signature).decode()

            if provided_signature != expected_signature:
                return {'error': 'Unauthorized request: Invalid signature'}

            # Validate branch
            branch = request.env['res.partner'].sudo().search(
                [('id', '=', branch_id), ('is_company', '=', True)],
                limit=1
            )
            if not branch:
                return {'error': 'Invalid Branch ID'}

            # Validate barcode
            partner = request.env['res.partner'].sudo().search([('barcode', '=', barcode_number)], limit=1)
            if not partner:
                return {'error': 'Invalid Barcode: No matching user found'}

            return {
                'CustomerFirstName': partner.name,
                'CustomerLastName': getattr(partner, 'last_name', ''),
                'OrganisationName': partner.parent_id.name if partner.parent_id else 'N/A',
                'Status': 'Active' if partner.active else 'Inactive'
            }

        except Exception as e:
            # Return a safe error message without exposing sensitive details
            return {'error': f"An unexpected error occurred: {str(e)}"}

    @http.route(
        ["/go/api/user/offers/v3"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_users_offer_list_v3(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [
                ("merchant_id", "!=", False),
                ("is_in_offer", "=", True),
                ("home_offer", "=", True),
            ]

            merchant_id = data.get("merchant_id")
            if merchant_id:
                domain += [
                    "|",
                    ("merchant_id", "=", merchant_id),
                    ("branch_ids", "in", merchant_id),
                ]

            merchant_category_id = data.get("merchant_category_id")
            if merchant_category_id:
                merchants = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("partner_category_id", "=", merchant_category_id)])
                )
                domain += [("merchant_id", "in", merchants.ids)]

            if data.get("x_offer_type"):
                domain += [("offer_type", "=", data["x_offer_type"])]

            if data.get("subscribed_merchant_offer"):
                lines = (
                    request.env["loyalty.notification.line"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", current_user.partner_id.id),
                            ("is_subscribe", "=", True),
                        ]
                    )
                )
                merchant_ids = lines.mapped("notification_id.merchant_id").ids
                if merchant_ids:
                    domain += [("merchant_id", "in", merchant_ids)]

            parent_partner_id = current_user.partner_id.parent_id.id
            if parent_partner_id:
                notin_app_ids = (
                    request.env["notin.app"]
                    .sudo()
                    .search([("parent_id", "=", parent_partner_id)])
                    .ids
                )
                domain += [("not_linked_app_ids", "not in", notin_app_ids)]

            limit = int(data.get("limit", 100000))
            offset = int(data.get("offset", 0))

            products = (
                request.env["product.template"]
                .sudo()
                .search_read(
                    domain,
                    [
                        "name",
                        "arabic_name",
                        "image_url",
                        "list_price",
                        "default_code",
                        "point",
                        "online_store",
                        "max_quantity",
                        "offer_type",
                        "offer_type_discount",
                        "offer_type_promo_code",
                        "merchant_online_store",
                        "buy_link",
                        "barcode",
                        "description",
                        "description_sale",
                        "description_arabic",
                        "offer_label",
                        "label_arabic",
                        "merchant_id",
                        "categ_id",
                        "create_date",
                        "start_date",
                        "end_date",
                        "min_quantity",
                        "discount",
                    ],
                    limit=limit,
                    offset=offset,
                )
            )

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            datas = []

            for product in products:
                product_template = (
                    request.env["product.template"].sudo().browse(product["id"])
                )
                merchant = product_template.merchant_id
                category_id = (
                    product["categ_id"][0] if product.get("categ_id") else False
                )
                category_name = (
                    product["categ_id"][1] if product.get("categ_id") else False
                )

                datas.append(
                    {
                        **product,
                        "ribbon": " ",
                        "merchant_name": merchant.name if merchant else False,
                        "merchant_id": merchant.id if merchant else False,
                        "merchant_name_arabic": (
                            merchant.arabic_name if merchant else False
                        ),
                        "phone_number": merchant.phone if merchant else False,
                        "mobile_number": merchant.mobile if merchant else False,
                        "merchant_email": merchant.email if merchant else False,
                        "merchant_rating": 4,
                        "category_id": category_id,
                        "category_name": category_name,
                        "disc_ribbon": product.get("offer_label"),
                        "point": product.get("point"),
                        "product_merchant_is_business_hotel": (
                            product.get("merchant_id"),
                        ),
                        "merchant_logo": url_join(
                            web_base_url,
                            (
                                f"/go/api/image/{merchant.id}/image_1920/res.partner"
                                if merchant
                                else ""
                            ),
                        ),
                    }
                )

            return datas

        except Exception as e:
            return {"error": str(e)}
