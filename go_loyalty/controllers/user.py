from odoo import http, fields, _
from odoo.http import request
import json
import ast
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
