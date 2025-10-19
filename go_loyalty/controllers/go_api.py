import json
from datetime import datetime
import requests
from odoo.http import request
from datetime import timedelta
from werkzeug.urls import url_join
from odoo import http, fields, _
import logging

from odoo.odoo.exceptions import AccessError, AccessDenied

_logger = logging.getLogger(__name__)


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
        [
            "/go/api/update/password",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_update_password(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            login = data.get("login")
            old_password = data.get("old_password")
            new_password = data.get("new_password")

            if not all([login, old_password, new_password]):
                return {"error": "Missing required parameters"}
            credential = {'login': login, 'password': old_password, 'type': 'password'}
            uid = request.session.authenticate(request.db, credential)
            if not uid:
                return {"error": "Old password is incorrect!", "status_code": "01"}

            user = request.env["res.users"].sudo().browse(uid.get('uid'))
            user.password = new_password
            request.session.logout()
            return {"success": "Password updated successfully", "status_code": "00"}

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        [
            "/ago/api/user/pass/update/v2",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def ago_api_update_password_v2(self, **post):
        res = {}
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            login = data.get("login")
            old_password = data.get("password")
            new_password = data.get("new_password")

            if not all([login, old_password, new_password]):
                return {"error": "Missing required parameters"}
            credential = {'login': login, 'password': old_password, 'type': 'password'}
            uid = request.session.authenticate(request.db, credential)
            if not uid:
                res['error'] = "Wrong password"
                return res

            user = request.env["res.users"].sudo().browse(uid.get('uid'))
            token = user.get_user_access_token()
            user.token = token
            user.password = data.get("new_password")
            res.update(
                password=data.get("new_password"),
                id=user.id,
                name=user.partner_id.name,
            )
            request.session.logout()
            return {"success": "Password updated successfully", "status_code": "00"}

        except AccessDenied:
            res['error'] = "Wrong password"
            return res
        except Exception as e:
            res['error'] = "Something Went Wrong! Kindly check current password  %s" % e
            return res

    @http.route(
        ["/go/api/user/email/check"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_user_email_check(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            email = data.get("email")
            if not email:
                return {"error": "Email missing"}

            if data.get("hayyakam"):
                if not email.endswith("@qr.com.qa"):
                    return {"error": "Kindly provide proper email under @qr.com.qa"}

            partner = (
                request.env["res.partner"]
                .sudo()
                .with_context(active_test=False)
                .search(
                    [
                        ("email", "=", email)
                    ],
                    limit=1,
                )
            )

            if partner:
                return {
                    "error": "User already exists with this email, try to reset the password!"
                }

            return {"success": "This email is not associated with any users yet!"}

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        ["/go/api/user/phone/check"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_user_phone_check(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            phone = data.get("phone")
            if not phone:
                return {"error": "Phone number missing"}

            partner = (
                request.env["res.partner"]
                .sudo()
                .search([("phone", "=", phone)], limit=1)
            )
            if partner:
                return {"error": "User already exists with this phone!"}

            return {"success": "This phone is not associated with any users yet!"}

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        ["/mobile/version_org"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_user_mobile_version_org(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            app_company_id = data.get("app_company_id")
            if not app_company_id:
                return {"error": "Company ID missing"}

            company = (
                request.env["res.partner"]
                .sudo()
                .search([("id", "=", app_company_id)], limit=1)
            )
            if not company:
                return {"error": "Version error: Company not found"}

            return {
                "success": "API for requested org, current mobile version",
                "current_mobile_version": company.mobile_version,
            }

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        ["/go/api/public/banner"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_public_banner(self, **post):
        try:
            banners = (
                request.env["advertisement.banner"]
                .sudo()
                .search([("tracking_code", "=", "Banner")])
            )
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            res = []

            for banner in banners:
                res.append(
                    {
                        "merchant_name": banner.name,
                        "banner_image": url_join(
                            web_base_url,
                            f"/go/api/image/{banner.id}/banner_image/advertisement.banner",
                        ),
                        "banner_url": banner.banner_url,
                        "sequence": banner.seq,
                    }
                )

            return res

        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    @http.route(
        ["/go/api/public/merchant"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_public_merchant(self, **post):
        try:
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            data = {
                "premium_merchants": self._get_premium_merchant_public(web_base_url)
            }
            return data
        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    def _get_premium_merchant_public(self, web_base_url):
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search_read(
                [
                    ("merchant_type", "=", "premium"),
                    ("premium_client", "=", True),
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
            merchant["merchant_logo"] = url_join(
                web_base_url, f'/go/api/image/{merchant["id"]}/image_512/res.partner'
            )

        return merchants

    @http.route(
        ["/go/api/public/popular/category"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_public_popular_category(self, **post):
        try:
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            data = {"popular_category": self._get_partner_category(web_base_url)}
            return data
        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    def _get_partner_category(self, web_base_url):
        categories = (
            request.env["partner.category"]
            .sudo()
            .search_read([], ["id", "name", "image_icon", "name_arabic"])
        )
        for cat in categories:
            cat["image_icon"] = url_join(
                web_base_url, f"/go/api/image/{cat['id']}/image_icon/partner.category"
            )
        return categories

    @http.route(
        ["/go/api/public/merchant/store"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_api_public_merchant_store(self, **post):
        try:
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            data = {
                "premium_merchants": self._get_premium_merchant_public_store(
                    web_base_url
                )
            }
            return data
        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    def _get_premium_merchant_public_store(self, web_base_url):
        merchants = (
            request.env["res.partner"]
            .sudo()
            .search_read(
                [
                    ("merchant_type", "=", "premium"),
                    ("premium_client", "=", True),
                ],
                [
                    "id",
                    "name",
                    "email",
                    "phone",
                    "website",
                    "partner_latitude",
                    "partner_longitude",
                    "merchant_rating",
                    "partner_category_id",
                ],
            )
        )
        for merchant in merchants:
            merchant["merchant_logo"] = url_join(
                web_base_url, f"/go/api/image/{merchant['id']}/image_512/res.partner"
            )
            merchant["merchant_banner"] = url_join(
                web_base_url, f"/go/api/image/{merchant['id']}/map_banner/res.partner"
            )
        return merchants

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

    @http.route(
        ["/go/api/gulfexc/notification/message/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_gulfexc_merchant_notification_message_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            NotificationList = request.env["loyalty.notification.list"].sudo()

            notifications = NotificationList.search(
                [("partner_id", "=", partner.id)], order="id desc"
            )

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            result = [
                {
                    "notification_id": n.id,
                    "merchant_id": n.merchant_id.id,
                    "merchant_name": n.merchant_id.name,
                    "partner_id": n.partner_id.id,
                    "partner_name": n.partner_id.name,
                    "product_id": n.product_id.id or False,
                    "description": n.description,
                    "html_description": n.description_html,
                    "notification_type": n.notification_type,
                    "state": n.state,
                    "date": (n.date + timedelta(hours=3)) if n.date else False,
                    "banner": url_join(
                        web_base_url,
                        f"/go/api/image/{n.merchant_id.id}/map_banner/res.partner",
                    ),
                    "merchant_logo": n.merchant_id.image_url,
                    "offer_image": url_join(
                        web_base_url,
                        f"/go/api/image/{n.id}/offer_image/loyalty.notification.list",
                    ),
                    "url_notification": n.url,
                }
                for n in notifications
            ]

            return result

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/premium/organisation"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_premium_organisation(self, **post):
        try:
            domain = [("entity_type", "=", "organisation"), ("is_published", "=", True)]
            organisations = request.env["res.partner"].sudo().search(domain)
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            res = []

            for partner in organisations:
                res.append(
                    {
                        "name": partner.name,
                        "id": partner.id,
                        "barcode": partner.barcode,
                        "map_banner": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/map_banner/res.partner",
                        ),
                        "merchant_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/image_512/res.partner",
                        ),
                        "category": (
                            partner.partner_category_id.name
                            if partner.partner_category_id
                            else ""
                        ),
                        "category_logo": (
                            url_join(
                                web_base_url,
                                f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
                            )
                            if partner.partner_category_id
                            else ""
                        ),
                        "banners": self._get_banners(partner, web_base_url),
                    }
                )
            return res
        except Exception as e:
            return {"error": f"Something went wrong: {str(e)}"}

    def _get_banners(self, partner, web_base_url):
        banners = (
            request.env["merchant.banner"]
            .sudo()
            .search_read(
                [("partner_id", "=", partner.id)],
                ["id", "name", "merchant_rating", "sequence"],
            )
        )
        for banner in banners:
            banner["banner_image"] = url_join(
                web_base_url, f"/go/api/image/{banner['id']}/image_1920/merchant.banner"
            )
        return banners

    @http.route(
        ["/go/api/save/offer/as/favourites"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def set_offer_as_favourites(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            product_id = data.get("product_id")
            if not product_id:
                return {"error": _("Product id missing")}

            product = request.env["product.template"].sudo().browse(int(product_id))
            if not product.exists():
                return {"error": _("Product not found")}

            partner_id = current_user.partner_id.id
            vals = {
                "is_save": data.get("is_save"),
                "is_voucher": data.get("is_voucher"),
                "partner_id": partner_id,
            }

            fav = product.favourite_partner_ids.filtered(
                lambda l: l.partner_id.id == partner_id
            )
            if fav:
                fav.sudo().write(vals)
            else:
                product.sudo().write({"favourite_partner_ids": [(0, 0, vals)]})

            return {"success": _("Successfully added to favourite list")}
        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/save/offer/as/favourite"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def set_offer_as_favourite(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            product_id = data.get("product_id")
            if not product_id:
                return {"error": _("Product ID missing")}

            product = request.env["product.template"].sudo().browse(int(product_id))
            if not product.exists():
                return {"error": _("Product not found")}

            partner_id = current_user.partner_id.id
            vals = {
                "is_save": data.get("is_save"),
                "is_voucher": data.get("is_voucher"),
                "partner_id": partner_id,
            }

            fav = product.favourite_partner_ids.filtered(
                lambda l: l.partner_id.id == partner_id
            )

            if vals["is_save"]:
                if fav:
                    fav.sudo().write(vals)
                else:
                    product.sudo().write({"favourite_partner_ids": [(0, 0, vals)]})
                return {"success": _("Successfully added to favourite list")}
            else:
                if fav:
                    fav.sudo().unlink()
                    return {"success": _("Successfully removed from favourite list")}
                else:
                    return {"info": _("No favourite record to remove")}
        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/restro/merchant"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_restro_merchant(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [("entity_type", "=", "merchant"), ("is_restro", "=", True)]
            merchants = request.env["res.partner"].sudo().search(domain)

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            PartnerCategory = request.env["partner.category"].sudo()

            res = []
            for partner in merchants:
                category = partner.partner_category_id
                category_name = category.name if category else ""
                category_logo = (
                    url_join(
                        web_base_url,
                        f"/go/api/image/{category.id}/image_icon/partner.category",
                    )
                    if category
                    else ""
                )

                res.append(
                    {
                        "merchant_name": partner.name,
                        "merchant_id": partner.id,
                        "barcode": partner.barcode,
                        "partner_latitude": partner.partner_latitude,
                        "partner_longitude": partner.partner_longitude,
                        "rating": partner.merchant_rating,
                        "map_banner": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/map_banner/res.partner",
                        ),
                        "merchant_logo": url_join(
                            web_base_url,
                            f"/go/api/image/{partner.id}/image_512/res.partner",
                        ),
                        "category": category_name,
                        "category_logo": category_logo,
                        "banners": self._get_banners(partner, web_base_url),
                    }
                )

            return res

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/get/favourite/products"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_offer_favourite_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner_id = current_user.partner_id.id
            domain = [
                ("favourite_partner_ids.partner_id", "=", partner_id),
                ("favourite_partner_ids.is_save", "=", True),
            ]

            if data.get("is_voucher"):
                domain += [("favourite_partner_ids.is_voucher", "=", True)]

            fields = [
                "name",
                "arabic_name",
                "merchant_id",
                "image_url",
                "list_price",
                "default_code",
                "barcode",
                "description",
                "description_sale",
                "label_arabic",
                "offer_label",
                "start_date",
                "end_date",
                "min_quantity",
                "max_quantity",
                "offer_type",
                "discount",
                "offer_type_promo_code",
            ]

            products = (
                request.env["product.template"].sudo().search_read(domain, fields)
            )
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            res = []

            Partner = request.env["res.partner"].sudo()
            for product in products:
                merchant_info = product.get("merchant_id")
                if (
                    merchant_info
                    and isinstance(merchant_info, (list, tuple))
                    and merchant_info[0]
                ):
                    merchant_id = merchant_info[0]
                    product["merchant_id"] = merchant_id
                    product["merchant_name"] = merchant_info[1] or ""
                    merchant = Partner.browse(merchant_id)
                    product["merchant_name_arabic"] = merchant.arabic_name
                    product["merchant_logo"] = url_join(
                        web_base_url,
                        f"/go/api/image/{merchant_id}/image_1920/res.partner",
                    )
                else:
                    product["merchant_id"] = False
                    product["merchant_name"] = ""
                    product["merchant_name_arabic"] = ""
                    product["merchant_logo"] = ""

                res.append(product)

            return res
        except Exception as e:
            return {"error": str(e)}

    @http.route(
        [
            "/go/api/get/favourite/products/gift",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_offer_favourite_list_gift(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [("offer_type", "=", "giftcard")]
            fields = [
                "name",
                "merchant_id",
                "image_url",
                "list_price",
                "default_code",
                "barcode",
                "description",
                "description_sale",
                "offer_label",
                "start_date",
                "end_date",
                "min_quantity",
                "max_quantity",
                "discount",
                "offer_type_promo_code",
            ]

            products = (
                request.env["product.template"].sudo().search_read(domain, fields)
            )
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            Partner = request.env["res.partner"].sudo()
            datas = []

            for product in products:
                merchant_info = product.get("merchant_id")
                if (
                    merchant_info
                    and isinstance(merchant_info, (list, tuple))
                    and merchant_info[0]
                ):
                    merchant_id = merchant_info[0]
                    product["merchant_id"] = merchant_id
                    product["merchant_name"] = merchant_info[1] or ""
                    product["merchant_logo"] = url_join(
                        web_base_url,
                        f"/go/api/image/{merchant_id}/image_1920/res.partner",
                    )
                else:
                    product["merchant_id"] = False
                    product["merchant_name"] = ""
                    product["merchant_logo"] = ""

                datas.append(product)

            return datas
        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/restro/category"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_restro_category(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            categories = request.env["loyalty.restaurant.category"].sudo().search([])
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )

            res = []
            for cat in categories:
                parent = cat.parent_id
                res.append(
                    {
                        "id": cat.id,
                        "name": cat.name,
                        "complete_name": cat.complete_name,
                        "name_arabic": cat.name_arabic,
                        "parent_id": parent.id if parent else False,
                        "parent_name": parent.name if parent else "",
                        "image": url_join(
                            web_base_url,
                            f"/go/api/image/{cat.id}/image_1920/loyalty.restaurant.category",
                        ),
                    }
                )

            return res

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/gif/binary/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_api_gif_binary(self, **post):
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

            categories = (
                request.env["partner.category"]
                .sudo()
                .search_read([], ["name", "name_arabic", "parent_id", "gif_image"])
            )

            res = []
            for cat in categories:
                parent = cat.get("parent_id")
                res.append(
                    {
                        "id": cat["id"],
                        "name": cat["name"],
                        "name_arabic": cat.get("name_arabic"),
                        "parent_id": parent[0] if parent else False,
                        "parent_name": parent[1] if parent else "",
                        "gif_image": url_join(
                            web_base_url,
                            f"/go/api/image/{cat['id']}/gif_image/partner.category",
                        ),
                    }
                )

            return res

        except Exception as e:
            return {"error": str(e)}

    # Todo
    @http.route(
        "/go/api/send_redemption_email",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def send_redemption_email(self, **post):
        """
        API Endpoint to send an email when an offer is redeemed.
        Expected parameters:
        - token (str)                 <-- required (validated via _validate_token)
        - merchant_name (str)
        - merchant_email (str)
        - offer_type (str)
        - product_name (str)
        - date (str)
        - time (str)
        - location_name (str)
        - confirmation_number (str)
        """
        try:
            # Standardized request parsing (same as other routes)
            data = post or self._get_json_request()
            if isinstance(data, dict) and "error" in data:
                return {"status": "error", "message": data["error"]}

            # Token validation (same helper you already use everywhere)
            user = self._validate_token(data)
            if isinstance(user, dict):  # error dict
                return {"status": "error", "message": user["error"]}

            # Extract params (strip whitespace where relevant)
            merchant_name = (data.get("merchant_name") or "").strip()
            merchant_email = (data.get("merchant_email") or "").strip()
            offer_type = (data.get("offer_type") or "").strip()
            product_name = (data.get("product_name") or "").strip()
            redemption_date = (data.get("date") or "").strip()
            redemption_time = (data.get("time") or "").strip()
            location_name = (data.get("location_name") or "").strip()
            confirmation_number = (data.get("confirmation_number") or "").strip()

            # Mandatory field check (same response shape you use elsewhere)
            required = {
                "merchant_name": merchant_name,
                "merchant_email": merchant_email,
                "offer_type": offer_type,
                "product_name": product_name,
                "date": redemption_date,
                "time": redemption_time,
                "location_name": location_name,
                "confirmation_number": confirmation_number,
            }
            missing = [
                k.replace("_", " ").capitalize() for k, v in required.items() if not v
            ]
            if missing:
                return {"status": "error", "message": "All fields are mandatory."}

            # Resolve CC from partner, then append default
            email_cc = "info@golalita.com"
            partner = (
                request.env["res.partner"]
                .sudo()
                .search([("email", "=", merchant_email)], limit=1)
            )
            if partner and getattr(partner, "cc_emails_management", False):
                # Normalize: dedupe, collapse whitespace, ensure comma separated
                cc_list = [
                    e.strip()
                    for e in f"{partner.cc_emails_management},info@golalita.com".split(
                        ","
                    )
                    if e.strip()
                ]
                # remove duplicates while preserving order
                seen = set()
                cc_norm = []
                for e in cc_list:
                    if e.lower() not in seen:
                        seen.add(e.lower())
                        cc_norm.append(e)
                email_cc = ",".join(cc_norm)

            # Subject/body – keep strings identical in spirit (no template dependency)
            email_subject = "Offer Redemption Notification"
            email_body = f"""
                <html>
                <body>
                    <p>Dear {merchant_name},</p>
                    <p>This is to notify you that a customer has redeemed an offer at your location:</p>
                    <div style="background:#f8f8f8;padding:15px;border-radius:6px;">
                        <p><strong>Location:</strong> {location_name}</p>
                        <p><strong>Offer Type:</strong> {offer_type}</p>
                        <p><strong>Product Name:</strong> {product_name}</p>
                        <p><strong>Date:</strong> {redemption_date}</p>
                        <p><strong>Time:</strong> {redemption_time}</p>
                    </div>
                    <p style="font-size:18px;font-weight:bold;color:#d9534f;text-align:center;">
                        Confirmation Number: {confirmation_number}
                    </p>
                    <p>If you have any questions, please feel free to contact us.</p>
                    <p>Best regards,<br><strong>Golalita</strong></p>
                </body>
                </html>
                """.strip()

            vals = {
                "subject": email_subject,
                "body_html": email_body,
                "email_to": merchant_email,
                "email_cc": email_cc,
                "auto_delete": False,
                "email_from": "support@golalita.com",
            }

            mail = request.env["mail.mail"].sudo().create(vals)
            # send() returns True/False; we’ll log but keep response shape the same
            sent = mail.sudo().send()
            _logger.info(
                "Redemption email %s to %s (cc=%s)",
                "SENT" if sent else "QUEUED",
                merchant_email,
                email_cc,
            )
            return {"status": "success", "message": "Email sent successfully"}

        except Exception as e:
            # Rollback and log internally; don’t leak stack details to client
            _logger.warning("Failed to send redemption email: %s", e)

    @http.route(
        "/go/api/send_redemption_email",
        type="json",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def send_redemption_email(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = [
                "merchant_name",
                "merchant_email",
                "offer_type",
                "product_name",
                "date",
                "time",
                "location_name",
                "confirmation_number",
            ]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {
                    "status": "error",
                    "message": _("Missing fields: %s") % ", ".join(missing),
                }

            merchant_name = data.get("merchant_name")
            merchant_email = data.get("merchant_email")
            offer_type = data.get("offer_type")
            product_name = data.get("product_name")
            redemption_date = data.get("date")
            redemption_time = data.get("time")
            location_name = data.get("location_name")
            confirmation_number = data.get("confirmation_number")

            email_cc = "info@golalita.com"
            partner = (
                request.env["res.partner"]
                .sudo()
                .search([("email", "=", merchant_email)], limit=1)
            )
            if partner and partner.cc_emails_management:
                email_cc = f"{partner.cc_emails_management},info@golalita.com"

            email_subject = "Offer Redemption Notification"
            email_body = f"""
                            <html>
                            <body>
                                <p>Dear {merchant_name},</p>
                                <p>This is to notify you that a customer has redeemed an offer at your location:</p>
                                <div style="background:#f8f8f8;padding:15px;border-radius:6px;">
                                    <p><strong>Location:</strong> {location_name}</p>
                                    <p><strong>Offer Type:</strong> {offer_type}</p>
                                    <p><strong>Product Name:</strong> {product_name}</p>
                                    <p><strong>Date:</strong> {redemption_date}</p>
                                    <p><strong>Time:</strong> {redemption_time}</p>
                                </div>
                                <p style="font-size:18px;font-weight:bold;color:#d9534f;text-align:center;">
                                    Confirmation Number: {confirmation_number}
                                </p>
                                <p>If you have any questions, please feel free to contact us.</p>
                                <p>Best regards,<br><strong>Golalita</strong></p>
                            </body>
                            </html>
                        """

            vals = {
                "subject": email_subject,
                "body_html": email_body,
                "email_to": merchant_email,
                "email_cc": email_cc,
                "auto_delete": False,
                "email_from": "support@golalita.com",
            }

            mail = request.env["mail.mail"].sudo().create(vals)
            mail.sudo().send()
            return {"status": "success", "message": _("Email sent successfully.")}
        except Exception as e:
            return {
                "status": "error",
                "message": _("An unexpected error occurred: %s") % str(e),
            }

    @http.route(
        "/go/api/gulfexc/change_password",
        auth="public",
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def gulf_exc_change_password(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        secret_key = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("gulfexc.secret_key", default="e9e6b0138afe1c861d7c9d3af96e33d3")
        )
        if data.get("secret_key") != secret_key:
            return {"error": _("Invalid secret key.")}

        login = data.get("login")
        new_password = data.get("new_password")

        if not login or not new_password:
            missing = [f for f in ["login", "new_password"] if not data.get(f)]
            return {"error": _("Missing fields: %s") % ", ".join(missing)}

        user = request.env["res.users"].sudo().search([("login", "=", login)], limit=1)
        if not user:
            return {"error": _("User not found.")}

        try:
            user.sudo().write({"password": new_password})
            return {"success": _("Password changed successfully.")}
        except Exception as e:
            return {"error": _("Failed to change password: %s") % str(e)}

    @http.route(
        [
            "/go/api/golalta/passcard/v3",
            "/go/api/golalta/passcard/v2",
        ],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_api_passcard_api_v3(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            IrConfigParam = request.env["ir.config_parameter"].sudo()
            username = (
                IrConfigParam.get_param("golalta_passcard_username") or "golalita"
            )
            password = (
                IrConfigParam.get_param("golalta_passcard_password")
                or "B_I9XNXsPGhYf5wNOPlL7w"
            )
            url = (
                IrConfigParam.get_param("golalta_passcard_url")
                or "https://api.passworks.io/v2/coupons/da60dcfb-69cb-494b-a8c8-8cf30e2f0806/passes"
            )

            label1 = data.get("key_label1")
            label2 = data.get("key_label2")
            barcode = data.get("barcode")

            headers = {"Content-Type": "application/json"}
            payload = {
                "pass": {
                    "secondary_fields": [
                        {"key": "5e8328", "label": "Name", "value": label1},
                        {"key": "5b3ec0", "label": "Date Exp", "value": label2},
                    ],
                    "barcodes": [
                        {"format": "ean128", "message": barcode, "alt_text": barcode}
                    ],
                }
            }

            response = requests.post(
                url, json=payload, headers=headers, auth=(username, password)
            )
            api_data = response.json()

            res = [
                {
                    "page_url": api_data.get("page_url"),
                    "pkpass_url": api_data.get("pkpass_url"),
                    "page_short_url": api_data.get("page_short_url"),
                    "pkpass_short_url": api_data.get("pkpass_short_url"),
                }
            ]
            return res

        except Exception as e:
            return {"error": str(e)}

    # Todo x_local_global fields is not defined in partner.category model in odoo 14.
    # @http.route(
    #     ["/go/api/child/category/v2/v3"],
    #     auth="public",
    #     website=True,
    #     methods=["POST"],
    #     csrf=False,
    #     type="json",
    # )
    # def get_api_parent_child_category_v3(self, **post):
    #     try:
    #         data = post or self._get_json_request()
    #         if "error" in data:
    #             return data
    #
    #         current_user = self._validate_token(data)
    #         if isinstance(current_user, dict):
    #             return current_user
    #
    #         parent_id = data.get("parent_id")
    #         domain = [("parent_id", "=", parent_id)]
    #
    #         type_filter = data.get("type")
    #         if type_filter == "local":
    #             domain.append(("x_local_global", "=", True))
    #         elif type_filter == "global":
    #             domain.append(("x_local_global", "=", False))
    #
    #         country_code = data.get("country")
    #         if country_code:
    #             country = (
    #                 request.env["res.country"]
    #                 .sudo()
    #                 .search([("code", "=", country_code)], limit=1)
    #             )
    #             if country:
    #                 domain.append(("x_country_ids_m2m", "in", country.id))
    #
    #         categories = (
    #             request.env["partner.category"]
    #             .sudo()
    #             .search_read(
    #                 domain, ["name", "image_icon", "x_name_arabic", "parent_id"]
    #             )
    #         )
    #
    #         web_base_url = (
    #             request.env["ir.config_parameter"]
    #             .sudo()
    #             .get_param("web.base.url", default="https://www.golalita.com")
    #         )
    #
    #         for cat in categories:
    #             for img_field in ["image_icon", "x_image2", "x_image3", "x_image4"]:
    #                 cat[img_field] = url_join(
    #                     web_base_url,
    #                     f"/go/api/image/{cat['id']}/{img_field}/partner.category",
    #                 )
    #
    #         return categories
    #
    #     except Exception as e:
    #         return {"error": str(e)}

    @http.route(
        ["/go/api/child/category/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_api_parent_child_category_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            parent_id = data.get("parent_id")
            domain = [("parent_id", "=", parent_id)]

            if data.get("type") == "local":
                domain.append(("global_local", "=", True))
            elif data.get("type") == "global":
                domain.append(("global_local_global", "=", True))

            if data.get("country"):
                country = (
                    request.env["res.country"]
                    .sudo()
                    .search([("code", "=", data.get("country"))], limit=1)
                )
                if country:
                    domain.append(("country_ids_m2m", "in", [country.id]))

            if data.get("org_id"):
                parent = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("id", "=", data.get("org_id"))], limit=1)
                )
                if parent:
                    domain.append(("organisation_ids", "in", [parent.id]))

            categories = (
                request.env["partner.category"]
                .sudo()
                .search_read(domain, ["name", "image_icon", "name_arabic", "parent_id"])
            )

            web_base_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url", default="https://www.golalita.com")
            )

            for cat in categories:
                cat["image_icon"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image_icon/partner.category",
                )
                cat["image2"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image2/partner.category",
                )
                cat["image3"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image3/partner.category",
                )
                cat["image4"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image4/partner.category",
                )

            return categories

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/parent/category/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_api_parent_category_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [('parent_id', '=', False)]

            if data.get("type") == "local":
                domain.append(("global_local", "=", True))
            elif data.get("type") == "global":
                domain.append(("global_local_global", "=", True))

            if data.get("country"):
                country = (
                    request.env["res.country"]
                    .sudo()
                    .search([("code", "=", data.get("country"))], limit=1)
                )
                if country:
                    domain.append(("country_ids_m2m", "in", [country.id]))

            if data.get("org_id"):
                parent = (
                    request.env["res.partner"]
                    .sudo()
                    .search([("id", "=", data.get("org_id"))], limit=1)
                )
                if parent:
                    domain.append(("organisation_ids", "in", [parent.id]))

            categories = (
                request.env["partner.category"]
                .sudo()
                .search_read(domain, ["name", "image_icon", "name_arabic", "parent_id"])
            )

            web_base_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url", default="https://www.golalita.com")
            )

            for cat in categories:
                cat["image_icon"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image_icon/partner.category",
                )
                cat["image2"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image2/partner.category",
                )
                cat["image3"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image3/partner.category",
                )
                cat["image4"] = url_join(
                    web_base_url,
                    f"/go/api/image/{cat['id']}/image4/partner.category",
                )

            return categories

        except Exception as e:
            return {"error": str(e)}

    @http.route(
        ["/go/api/get/favourite/merchants"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_favourite_merchants(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            if not data.get("customer_id"):
                return {"error": _("Customer ID is missing")}

            customer = (
                request.env["res.partner"]
                .sudo()
                .search([("id", "=", data["customer_id"])], limit=1)
            )
            if not customer:
                return {"error": _("Customer not found")}

            favourite_records = (
                request.env["favourite.product"]
                .sudo()
                .search(
                    [("partner_id", "=", customer.id), ("fav_merchant_id", "!=", False)]
                )
            )

            merchant_ids = favourite_records.mapped("fav_merchant_id").ids
            if not merchant_ids:
                return {"merchants": []}

            merchants = (
                request.env["res.partner"].sudo().search([("id", "in", merchant_ids)])
            )
            web_base_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url", default="https://www.golalita.com")
            )

            res = []
            for partner in merchants:
                res.append(
                    {
                        "merchant_name": partner.name,
                        "x_arabic_name": partner.arabic_name,
                        "merchant_id": partner.id,
                        "x_for_employee_type": partner.employee_type,
                        "is_business_hotel": partner.is_hotel_type,
                        "x_moi_show": partner.show_in_moi,
                        "x_have_branch": partner.has_branches,
                        "x_have_offers": partner.has_offers,
                        "accept_go_loyalty_point": partner.go_loyalty_point,
                        "open_from": partner.open_from,
                        "open_till": partner.open_till,
                        "x_kts": partner.kts,
                        "x_org_linked": partner.org_type,
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
                            web_base_url,
                            f"/web/binary/contract_download_pdf/{partner.id}",
                        ),
                        "company_registration_url": url_join(
                            web_base_url,
                            f"/web/binary/registration_download_pdf/{partner.id}",
                        ),
                    }
                )

            return {"merchants": res}

        except Exception as e:
            return {"error": f"Error occurred: {str(e)}"}

    @http.route(
        ["/go/api/remove/favourite/merchant"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def remove_favourite_merchant(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            for field in ["customer_id", "merchant_id"]:
                if not data.get(field):
                    return {
                        "error": _(f'{field.replace("_", " ").capitalize()} is missing')
                    }

            customer = (
                request.env["res.partner"]
                .sudo()
                .search([("id", "=", data["customer_id"])], limit=1)
            )
            if not customer:
                return {"error": _("Customer not found")}

            favourite_record = (
                request.env["favourite.product"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", customer.id),
                        ("fav_merchant_id", "=", data["merchant_id"]),
                    ],
                    limit=1,
                )
            )

            if not favourite_record:
                return {"error": _("Favourite merchant record not found")}

            favourite_record.sudo().unlink()

            updated_ids = (
                request.env["favourite.product"]
                .sudo()
                .search([("partner_id", "=", customer.id)])
                .mapped("fav_merchant_id")
                .ids
            )

            if not updated_ids:
                return {"merchants": []}

            merchants = (
                request.env["res.partner"].sudo().search([("id", "in", updated_ids)])
            )
            web_base_url = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url")
            )
            res = []

            for partner in merchants:
                res.append(
                    {
                        "merchant_name": partner.name,
                        "merchant_id": partner.id,
                        "x_for_employee_type": partner.employee_type,
                        "is_business_hotel": partner.is_hotel_type,
                        "x_moi_show": partner.show_in_moi,
                        "x_have_branch": partner.has_branches,
                        "x_have_offers": partner.has_offers,
                        "accept_go_loyalty_point": partner.go_loyalty_point,
                        "open_from": partner.open_from,
                        "open_till": partner.open_till,
                        "x_kts": partner.kts,
                        "x_org_linked": partner.org_type,
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
                            web_base_url,
                            f"/web/binary/contract_download_pdf/{partner.id}",
                        ),
                        "company_registration_url": url_join(
                            web_base_url,
                            f"/web/binary/registration_download_pdf/{partner.id}",
                        ),
                    }
                )

            return {
                "success": _("Favourite merchant successfully removed"),
                "merchants": res,
            }

        except Exception as e:
            return {"error": f"Error occurred: {str(e)}"}
