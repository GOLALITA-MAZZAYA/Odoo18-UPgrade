from odoo import http, fields, _
from odoo.http import request
from werkzeug.urls import url_join
from datetime import timedelta,datetime
import json

class Advertisement(http.Controller):

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
        ["/go/api/advertisement/banner"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_org_details_adv(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            company = current_user.company_id
            if not company:
                return {"error": _("No company linked with this user")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                or ""
            )

            return {
                "ad_1": self._prepare_adv_data(company.ad_1_ids, web_base_url),
                "ad_2": self._prepare_adv_data(company.ad_2_ids, web_base_url),
                "ad_3": self._prepare_adv_data(company.ad_3_ids, web_base_url),
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    def _prepare_adv_data(self, ad_records, web_base_url):
        if not ad_records:
            return []

        return [
            {
                "name": ad.name,
                "banner_image": url_join(
                    web_base_url,
                    f"/go/api/image/{ad.id}/banner_image/advertisement.banner",
                ),
                "banner_url": ad.banner_url,
                "is_sjc": ad.sjc,
                "x_android": ad.android,
                "x_ios": ad.ios,
                "internal": ad.internal,
                "merchant_id": ad.merchant_id.id if ad.merchant_id else False,
                "sequence": ad.seq,
                "tracking_code": ad.tracking_code,
            }
            for ad in ad_records.filtered(lambda a: a.org_type == "golalita")
        ]

    @http.route(
        ["/go/api/advertisement_tracking"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_advert_tracking(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = [
                "customer",
                "customer_id",
                "email",
                "phone",
                "tracking_code",
                "date_time",
            ]
            for field in required_fields:
                if not data.get(field):
                    return {
                        "error": _(f"{field.replace('_', ' ').capitalize()} Missing")
                    }

            partner = (
                request.env["res.partner"]
                .sudo()
                .search([("id", "=", data["customer_id"])], limit=1)
            )
            if not partner:
                return {"error": _("Customer not found in the system")}

            def parse_date(date_str):
                if not date_str:
                    return False
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%m/%d/%Y %I:%M %p",
                    "%d-%m-%Y %H:%M:%S",
                    "%d/%m/%Y %H:%M",
                ]
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except Exception:
                        continue
                return False

            tracking_date = parse_date(data.get("date_time"))
            if not tracking_date:
                return {"error": _("Invalid date_time format")}

            tracking = (
                request.env["advertisement.tracking"]
                .sudo()
                .create(
                    {
                        "partner_id": partner.id,
                        "customer_name": data.get("customer"),
                        "email": data.get("email"),
                        "phone": data.get("phone"),
                        "tracking_code": data.get("tracking_code"),
                        "date": tracking_date,
                    }
                )
            )

            return {
                "success": _("Tracking updated successfully!"),
                "tracking_id": tracking.id,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/user/social/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_user_social(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            website = request.env["website"].get_current_website()
            social_media_links = [
                {
                    "social_facebook": website.social_facebook,
                    "social_linkedin": website.social_linkedin,
                    "social_twitter": website.social_twitter,
                    "social_instagram": website.social_instagram,
                }
            ]
            return social_media_links

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/code/check/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_api_code_check_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            code = data.get("code")
            if not code:
                return {"error": _("Code Missing")}

            orgs = (
                request.env["org.registration.code"]
                .sudo()
                .search([("code", "=", code)])
            )
            res = []

            for partner in orgs:
                org = request.env["res.partner"].sudo().browse(partner.partner_id.id)
                if org._is_registred(code):
                    return res

                res.append(
                    {
                        "org_name": partner.partner_id.name,
                        "code": partner.code,
                    }
                )

            return res

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}



    @http.route(
        ["/go/api/pause/notification"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def pause_notification(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            current_user.sudo().partner_id.write({"pause_notification": True})

            return {"success": "Successfully paused all notifications"}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/unpause/notification"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def unpause_notification(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            current_user.sudo().partner_id.write({"pause_notification": False})

            return {"success": "Successfully unpaused all notifications"}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}
