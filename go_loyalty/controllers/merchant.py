import json
import logging
from datetime import timedelta, datetime

from dateutil.relativedelta import relativedelta
from odoo.http import request
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from werkzeug.urls import url_join

from odoo import http, fields, _

_logger = logging.getLogger(__name__)


class Merchant(http.Controller):

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

    def _get_products_count(self, partner):
        try:
            return (
                request.env["product.template"]
                .sudo()
                .search_count([("merchant_id", "=", partner.id)])
            )
        except Exception:
            return 0

    def _get_offer_products_count(self, partner):
        try:
            return (
                request.env["product.template"]
                .sudo()
                .search_count(
                    [("merchant_id", "=", partner.id), ("is_in_offer", "=", True)]
                )
            )
        except Exception:
            return 0

    def _prepare_sale_data_list(self, sales):
        return [
            {
                "id": sale.id,
                "name": sale.name,
                "date": sale.date,
                "customer": sale.partner_id.name,
                "customer_logo": sale.partner_id.image_url,
                "discount": sale.discount,
                "points": sale.points,
                "type": sale.transfer_point_type,
                "amount": sale.amount,
            }
            for sale in sales
        ]

    def _prepare_notification_list(self, notifications, web_base_url):
        return [
            {
                "merchant_name": n.merchant_id.name,
                "merchant_name_arabic": n.merchant_id.arabic_name,
                "partner_id": n.partner_id.id,
                "product_id": n.product_id.id or False,
                "partner_name": n.partner_id.name,
                "description": n.description,
                "x_description_arabic": n.description_ar,
                "date": n.date + timedelta(hours=3),
                "notification_type": n.notification_type,
                "merchant_id": n.merchant_id.id,
                "banner": url_join(
                    web_base_url,
                    f"/go/api/image/{n.merchant_id.id}/map_banner/res.partner",
                ),
                "merchant_logo": n.merchant_id.image_url,
                "notification_id": n.id,
                "html_description": n.description_html,
                "html_description_arabic": n.description_html_arabic,
                "state": n.state,
                "offer_image": url_join(
                    web_base_url,
                    f"/go/api/image/{n.id}/offer_image/loyalty.notification.list",
                ),
                "url_notification": n.url,
                "imp_notification": n.imp_notification,
            }
            for n in notifications
        ]

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
            "organisation": partner.parent_id.name or "",
            "organisation_logo": (
                url_join(
                    web_base_url,
                    f"/go/api/image/{partner.parent_id.id}/image_512/res.partner",
                )
                if partner.parent_id
                else ""
            ),
            "photo": url_join(
                web_base_url, f"/go/api/image/{partner.id}/image_512/res.partner"
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

    def _prepare_hotel_enquiry_vals(self, data):

        def parse_date(field_name, fallback_field):
            val = data.get(field_name) or data.get(fallback_field)
            if not val:
                return False

            for fmt in ("%m/%d/%Y %I:%M %p", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(val, fmt).strftime(
                        DEFAULT_SERVER_DATE_FORMAT
                    )
                except Exception:
                    continue
            return False

        return {
            "name": data.get("name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "country": data.get("country"),
            "city": data.get("city"),
            "departure_date": parse_date("departure_date", "departure_date_f"),
            "return_date": parse_date("return_date", "return_date_f"),
            "no_adult": data.get("no_adult"),
            "no_children": data.get("no_children"),
            "hotel_name": data.get("hotel_name"),
            "note": data.get("note"),
            "product_id": data.get("product_id") or None,
            "partner_id": int(data.get("merchant_id")),
            "product_name": data.get("product_name") or None,
            "product_price": data.get("product_price") or None,
        }

    # def _get_notification_info(self, merchant_id, user_partner_id):
    #     Notification = request.env["loyalty.notification"].sudo()
    #     notification = Notification.search([("merchant_id", "=", merchant_id)], limit=1)
    #     if not notification:
    #         return {}
    #
    #     return {
    #         "notification_id": notification.id,
    #         "is_subscribed": getattr(notification, "_is_subscribed", lambda x: False)(
    #             user_partner_id
    #         ),
    #         "title": notification.name or "",
    #         "message": notification.message or "",
    #         "create_date": notification.create_date,
    #     }

    # def _prepare_merchant_data(self, partner, web_base_url, current_user):
    #     notif_data = self._get_notification_info(
    #         merchant_id=partner.id, user_partner_id=current_user.partner_id.id
    #     )
    #
    #     return {
    #         "create_date": partner.create_date,
    #         "x_for_employee_type": partner.x_for_employee_type,
    #         "merchant_name": partner.name,
    #         "x_have_branch": partner.x_have_branch,
    #         "x_have_offers": partner.x_have_offers,
    #         "is_business_hotel": partner.is_hotel_type,
    #         "x_moi_show": partner.x_moi_show,
    #         "x_kts": partner.x_kts,
    #         "merchant_id": partner.id,
    #         "accept_go_loyalty_point": partner.x_go_loyalty_point,
    #         "x_online_store": partner.x_online_store,
    #         "x_sequence": partner.x_sequence,
    #         "barcode": partner.barcode,
    #         "partner_latitude": partner.partner_latitude,
    #         "partner_longitude": partner.partner_longitude,
    #         "ribbon_text": partner.ribbon_text,
    #         "ribbon_color": partner.ribbon_color,
    #         "ribbon_position": partner.ribbon_position,
    #         "rating": partner.merchant_rating,
    #         "map_banner": url_join(
    #             web_base_url, f"/go/api/image/{partner.id}/map_banner/res.partner"
    #         ),
    #         "merchant_logo": url_join(
    #             web_base_url, f"/go/api/image/{partner.id}/image_512/res.partner"
    #         ),
    #         "category": partner.partner_category_id.name,
    #         "category_id": partner.partner_category_id.id,
    #         "country_id": partner.country_id.id,
    #         "country_code": partner.country_id.code,
    #         "country_name": partner.country_id.name,
    #         "category_logo": url_join(
    #             web_base_url,
    #             f"/go/api/image/{partner.partner_category_id.id}/image_icon/partner.category",
    #         ),
    #         "banners": self._get_banners(partner, web_base_url),
    #         "pdf_attached": partner.x_pdf_attached,
    #         "company_contract_url": url_join(
    #             web_base_url, f"/web/binary/contract_download_pdf/{partner.id}"
    #         ),
    #         "company_registartion_url": url_join(
    #             web_base_url, f"/web/binary/registration_download_pdf/{partner.id}"
    #         ),
    #         "notification": notif_data,
    #     }

    @http.route(
        ["/go/api/merchant/my/transaction"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_merchant_customer_transaction(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        partner = current_user.partner_id
        if partner.entity_type != "merchant":
            return {"error": _("You are not allowed to access this API")}

        try:
            sales = (
                request.env["loyalty.sale"]
                .sudo()
                .search([("merchant_id", "=", partner.id)])
            )
            result = self._prepare_sale_data_list(sales)
            return {"transactions": result}
        except Exception as e:
            return {"error": _("Failed to fetch merchant transactions: %s") % str(e)}

    @http.route(
        ["/go/api/merchant/my/customer/transaction"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def go_merchant_customer_individual(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        customer_id = data.get("customer_id")
        if not customer_id:
            return {"error": _("Customer ID Missing")}

        partner = current_user.partner_id
        if partner.entity_type != "merchant":
            return {"error": _("You are not allowed to access this API")}

        try:
            sales = (
                request.env["loyalty.sale"]
                .sudo()
                .search(
                    [("merchant_id", "=", partner.id), ("partner_id", "=", customer_id)]
                )
            )
            result = self._prepare_sale_data_list(sales)
            return {"transactions": result}
        except Exception as e:
            return {"error": _("Failed to fetch customer transactions: %s") % str(e)}

    @http.route(
        ["/go/api/merchant/transaction/data/by/date"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_transaction_by_date(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        current_user = self._validate_token(data)
        if isinstance(current_user, dict):
            return current_user

        from_date = data.get("from_date")
        to_date = data.get("to_date")
        if not from_date:
            return {"error": _("From date missing")}
        if not to_date:
            return {"error": _("To date missing")}

        partner = current_user.partner_id
        if partner.entity_type != "merchant":
            return {"error": _("You are not allowed to access this API")}

        try:
            transactions = (
                request.env["loyalty.point.transfer.line"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", partner.id),
                        ("date", ">=", from_date),
                        ("date", "<=", to_date),
                    ]
                )
            )

            total_points_rewards = sum(transactions.mapped("credit"))
            total_points_redeem = sum(transactions.mapped("debit"))
            total_available_points = total_points_rewards - total_points_redeem
            total_sales = sum(transactions.mapped("sale_id.amount"))
            total_products = self._get_products_count(partner)
            total_offer_products = self._get_offer_products_count(partner)

            return {
                "name": partner.name,
                "customer_logo": partner.image_url,
                "total_points_rewards": total_points_rewards,
                "total_points_redeem": total_points_redeem,
                "total_available_points": total_available_points,
                "total_sales": total_sales,
                "total_products": total_products,
                "total_offer_products": total_offer_products,
            }
        except Exception as e:
            return {
                "error": _("Failed to fetch merchant transaction data: %s") % str(e)
            }

    @http.route(
        ["/go/api/user/merchant/subscribe"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_subscribe(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            device_id = data.get("device_id")
            merchant_id = data.get("merchant_id")

            if not device_id:
                return {"error": _("Device ID missing")}
            if not merchant_id:
                return {"error": _("Merchant ID missing")}

            merchant = request.env["res.partner"].sudo().browse(int(merchant_id))
            if not merchant.exists() or merchant.entity_type != "merchant":
                return {"error": _("Provided merchant is not registered with us")}

            partner = current_user.partner_id

            notification = (
                request.env["loyalty.notification"]
                .sudo()
                .search([("merchant_id", "=", merchant.id)], limit=1)
            )
            if not notification:
                return {"error": _("No notification found for this merchant")}

            if not notification._is_subscribed(partner.id):
                notification._subscribe_user(partner, device_id)

            return {
                "success": _("Successfully subscribed to merchant %s") % merchant.name
            }

        except Exception as e:
            return {"error": _("Something went wrong while subscribing: %s") % str(e)}

    @http.route(
        ["/go/api/user/notification/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_notification_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            notifications = request.env["loyalty.notification"].sudo().search([])

            result = [
                {
                    "merchant_name": n.merchant_id.name,
                    "merchant_id": n.merchant_id.id,
                    "merchant_logo": n.merchant_id.image_url,
                    "merchant_category_logo": (
                        n.merchant_id.partner_category_id.image_url
                        if n.merchant_id.partner_category_id
                        else False
                    ),
                }
                for n in notifications
            ]
            return result

        except Exception as e:
            return {"error": _("Failed to fetch notifications: %s") % str(e)}

    @http.route(
        ["/go/api/user/merchant/branch/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_branch_list(self, **post):
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

            branches = (
                request.env["merchant.branch"]
                .sudo()
                .search([("partner_id", "=", int(merchant_id))])
            )

            result = [
                {
                    "name": branch.name,
                    "name_arabic": branch.name_ar,
                    "code": branch.code,
                    "merchant_id": branch.partner_id.id,
                    "merchant_sub_id": (
                        branch.partner_sub_id.id if branch.partner_sub_id else False
                    ),
                }
                for branch in branches
            ]

            return result

        except Exception as e:
            return {"error": _("Failed to fetch merchant branches: %s") % str(e)}

    @http.route(
        ["/go/api/user/notification/message/list"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_notification_message_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                or ""
            )
            notifications = (
                request.env["loyalty.notification.list"]
                .sudo()
                .search([("partner_id", "=", partner.id)], order="id desc")
            )

            return self._prepare_notification_list(notifications, web_base_url)

        except Exception as e:
            return {"error": _("Failed to fetch notifications: %s") % str(e)}

    @http.route(
        ["/go/api/user/notification/message/list/delete"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def remove_notification_message_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            notification_id = data.get("notification_id")
            if not notification_id:
                return {"error": _("Notification ID missing")}

            notifications = (
                request.env["loyalty.notification.list"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", current_user.partner_id.id),
                        ("id", "=", int(notification_id)),
                    ],
                    limit=1,
                )
            )
            if not notifications:
                return {"error": _("Notification not found!")}

            notifications.unlink()
            return {"success": _("Successfully deleted the notification!")}
        except Exception as e:
            return {
                "error": _("Something went wrong while deleting notification: %s")
                % str(e)
            }

    @http.route(
        ["/go/api/user/notification/list/read/status"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def mark_as_read_unread_notification(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            notification_id = data.get("notification_id")
            read_status = data.get("read_status")

            if not notification_id:
                return {"error": _("Notification ID missing")}
            if not read_status:
                return {"error": _("Read Status missing")}

            notification = (
                request.env["loyalty.notification.list"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", current_user.partner_id.id),
                        ("id", "=", int(notification_id)),
                    ],
                    limit=1,
                )
            )
            if not notification:
                return {"error": _("Notification not found!")}

            notification.state = read_status
            return {"success": _("Notification status updated successfully!")}

        except Exception as e:
            return {
                "error": _(
                    "Something went wrong while updating notification status: %s"
                )
                % str(e)
            }

    @http.route(
        ["/go/api/user/merchant/unsubscribe"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_unsubscribe(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            merchant_id = data.get("merchant_id")
            if not merchant_id:
                return {"error": _("Merchant ID missing")}

            merchant = request.env["res.partner"].sudo().browse(int(merchant_id))
            if not merchant.exists() or merchant.entity_type != "merchant":
                return {"error": _("Provided merchant is not registered with us")}

            partner = current_user.partner_id
            notification = (
                request.env["loyalty.notification"]
                .sudo()
                .search([("merchant_id", "=", merchant.id)], limit=1)
            )
            if not notification:
                return {"error": _("No notification channel found for this merchant")}

            if notification._is_subscribed(partner.id):
                notification._unsubscribe_user(partner)

            return {
                "success": _("Successfully unsubscribed from merchant %s")
                % merchant.name
            }

        except Exception as e:
            return {"error": _("Something went wrong while unsubscribing: %s") % str(e)}

    @http.route(
        ["/go/api/merchant/create/sales/transaction"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def create_get_sales_transaction(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = [
                "amount",
                "partner_id",
                "merchant_id",
                "transfer_point_type",
            ]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {"error": _("Missing required fields: %s") % ", ".join(missing)}

            vals = {
                "amount": data["amount"],
                "partner_id": int(data["partner_id"]),
                "merchant_id": int(data["merchant_id"]),
                "transfer_point_type": data["transfer_point_type"],
            }

            sale = request.env["loyalty.sale"].sudo().create(vals)

            return {
                "id": sale.id,
                "transaction_reference": sale.name,
                "amount": sale.amount,
                "partner_id": sale.partner_id.id,
                "transfer_point_type": sale.transfer_point_type,
                "rule": sale.rule_id.name if sale.rule_id else False,
                "point_earn": sale.points,
                "amount_to_pay": sale.final_amount,
                "customer_available_points": sale.partner_id.points,
                "customer_type": sale.partner_id.employee_type,
                "discount": sale.discount,
            }

        except Exception as e:
            return {
                "error": _("Something went wrong while creating transaction: %s")
                % str(e)
            }

    @http.route(
        ["/go/api/merchant/search/customer"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_customer_by_barcode(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            barcode = data.get("barcode")
            if not barcode:
                return {"error": _("Barcode missing")}

            if current_user.partner_id.entity_type != "merchant":
                return {"error": _("You are not allowed to access this API")}

            partner = (
                request.env["res.partner"]
                .sudo()
                .search(
                    [("barcode", "=", barcode), ("entity_type", "=", "employee")],
                    limit=1,
                )
            )
            if not partner:
                return {"error": _("Provided employee is not registered with us")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
                or ""
            )
            return self._get_partner_profile(partner, web_base_url)

        except Exception as e:
            return {
                "error": _("Something went wrong while fetching customer: %s") % str(e)
            }

    @http.route(
        ["/go/api/merchant/hotel/enquiry"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_hotel_enquiry(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            required_fields = ["merchant_id"]
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {"error": _("Missing required fields: %s") % ", ".join(missing)}

            merchant = (
                request.env["res.partner"]
                .sudo()
                .search(
                    [
                        ("id", "=", data["merchant_id"]),
                        ("entity_type", "=", "merchant"),
                    ],
                    limit=1,
                )
            )
            if not merchant:
                return {"error": _("Merchant not found in system")}

            enquiry_vals = self._prepare_hotel_enquiry_vals(data)
            enquiry = request.env["merchant.enquiry"].sudo().create(enquiry_vals)
            # enquiry.sudo().action_send_mail()

            return {"success": _("Enquiry submitted successfully")}

        except Exception as e:
            return {
                "error": _("Something went wrong while submitting enquiry: %s") % str(e)
            }

    @http.route(
        ["/go/api/count/merchant/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_count(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            merchant_id = data.get("merchant_id")
            if not merchant_id:
                return {"error": _("Merchant ID Not Provided")}

            return True

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/merchant/track/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def track_merchant_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = {
                "customer_name": _("Customer Information Missing"),
                "customer_id": _("Customer ID Missing"),
                "customer_email": _("Email Missing"),
                "customer_phone": _("Phone No. Missing"),
                "track_type": _("Tracking Type Missing"),
                "track_value": _("Track Value Missing"),
                "track_date_time": _("Date Time Missing"),
                "product_id": _("Product ID Missing"),
            }

            for field, message in required_fields.items():
                if not data.get(field):
                    return {"error": message}

            def parse_date(date_str):
                possible_formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                    "%d-%m-%Y %I:%M %p",
                    "%Y-%m-%d",
                    "%d-%m-%Y",
                ]
                for fmt in possible_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except Exception:
                        continue
                return None

            track_date = parse_date(data["track_date_time"])
            if not track_date:
                return {"error": _("Invalid date format for track_date_time")}

            partner = request.env["res.partner"].sudo().browse(int(data["customer_id"]))
            if not partner.exists():
                return {"error": _("Customer not found in the system")}

            # tracking = (
            #     request.env["advertisement.tracking"]
            #     .sudo()
            #     .create(
            #         {
            #             "partner_id": partner.id,
            #             "customer_name": data["customer_name"],
            #             "email": data["customer_email"],
            #             "phone": data["customer_phone"],
            #             "tracking_code": data["track_value"],
            #             "date": track_date,
            #         }
            #     )
            # )

            return {
                "success": _("Tracking updated successfully !!"),
                "tracking_id": partner.id,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/go/api/save/merchant/as/favourite"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def set_merchant_as_favourite(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = {
                "customer_id": "Customer ID is missing",
                "merchant_id": "Merchant ID is missing",
            }
            for field, message in required_fields.items():
                if not data.get(field):
                    return {"error": _(message)}

            # Fetch customer and merchant once
            customer = (
                request.env["res.partner"].sudo().browse(int(data["customer_id"]))
            )
            if not customer.exists():
                return {"error": _("Customer not found")}

            merchant = (
                request.env["res.partner"].sudo().browse(int(data["merchant_id"]))
            )
            if not merchant.exists():
                return {"error": _("Merchant not found")}

            vals = {
                "partner_id": customer.id,
                "fav_merchant_id": merchant.id,
            }

            favourite_record = (
                request.env["favourite.product"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", customer.id),
                        ("fav_merchant_id", "=", merchant.id),
                    ],
                    limit=1,
                )
            )

            if favourite_record:
                favourite_record.sudo().write(vals)
            else:
                request.env["favourite.product"].sudo().create(vals)

            return {"success": _("Merchant successfully added to favourite list")}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/ago/api/get/favourite/merchants"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_favourite_merchants_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            customer_id = data.get("customer_id")
            if not customer_id:
                return {"error": _("Customer ID is missing")}

            customer = request.env["res.partner"].sudo().browse(int(customer_id))
            if not customer.exists():
                return {"error": _("Customer not found")}

            favourite_records = (
                request.env["favourite.product"]
                .sudo()
                .search(
                    [("partner_id", "=", customer.id), ("fav_merchant_id", "!=", False)]
                )
            )

            merchant_ids = favourite_records.mapped("fav_merchant_id").ids

            return {"merchant_ids": merchant_ids}

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    @http.route(
        ["/ago/api/remove/favourite/merchant"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def remove_favourite_merchant_v2(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            required_fields = {
                "customer_id": _("Customer ID is missing"),
                "merchant_id": _("Merchant ID is missing"),
            }
            for field, message in required_fields.items():
                if not data.get(field):
                    return {"error": message}

            customer = (
                request.env["res.partner"].sudo().browse(int(data["customer_id"]))
            )
            if not customer.exists():
                return {"error": _("Customer not found")}

            favourite_record = (
                request.env["favourite.product"]
                .sudo()
                .search(
                    [
                        ("partner_id", "=", customer.id),
                        ("fav_merchant_id", "=", int(data["merchant_id"])),
                    ],
                    limit=1,
                )
            )
            if not favourite_record:
                return {"error": _("Favourite merchant record not found")}

            favourite_record.sudo().unlink()

            updated_favourite_records = (
                request.env["favourite.product"]
                .sudo()
                .search([("partner_id", "=", customer.id)])
            )
            updated_merchant_ids = updated_favourite_records.mapped(
                "fav_merchant_id"
            ).ids

            return {
                "success": _("Favourite merchant successfully removed"),
                "merchant_ids": updated_merchant_ids,
            }

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    # @http.route(
    #     ["/go/api/user/merchant/lists"],
    #     auth="public",
    #     website=True,
    #     methods=["POST"],
    #     csrf=False,
    #     type="json",
    #     cors="*",
    # )
    # def get_user_merchant_list_v3(self, **post):
    #     try:
    #         # Parse request data
    #         data = post or self._get_json_request()
    #         if "error" in data:
    #             return data
    #
    #         # Validate token
    #         current_user = self._validate_token(data)
    #         if isinstance(current_user, dict):
    #             return current_user
    #
    #         # Base domain
    #         app = (
    #             request.env["notin.app"]
    #             .sudo()
    #             .search([("parent_id", "=", current_user.parent_id.id)], limit=1)
    #         )
    #         app_id = [app.id] if app else []
    #         domain = [
    #             ("entity_type", "=", "merchant"),
    #             ("active", "=", True),
    #             ("not_linked_ids", "not in", app_id),
    #         ]
    #
    #         # --- Simplified filter logic ---
    #         field_map = {
    #             "category_id": ("partner_category_id", "child_of"),
    #             "country_id": ("country_id", "="),
    #             "merchant_name": ("name", "="),
    #             "merchant_type": ("merchant_type", "="),
    #             "merchant_id": ("id", "="),
    #             "x_org_linked": ("x_org_linked", "="),
    #         }
    #
    #         domain += [
    #             (field, operator, data[key])
    #             for key, (field, operator) in field_map.items()
    #             if data.get(key)
    #         ]
    #
    #         # Pagination
    #         offset = int(data.get("offset", 0))
    #         limit = int(data["limit"]) if data.get("limit") else None
    #
    #         # Search merchants
    #         merchants = (
    #             request.env["res.partner"]
    #             .sudo()
    #             .search(
    #                 domain, order="create_date, x_sequence", offset=offset, limit=limit
    #             )
    #         )
    #
    #         # Base URL
    #         web_base_url = (
    #             request.env["ir.config_parameter"].sudo().get_param("web.base.url")
    #         )
    #
    #         # Prepare merchant data (using helper)
    #         result = [
    #             self._prepare_merchant_data(partner, web_base_url, current_user)
    #             for partner in merchants
    #         ]
    #
    #         return result
    #
    #     except Exception as e:
    #         return {"error": _("Something went wrong: %s") % str(e)}

    # Todo check again with all domain
    @http.route(
        ["/go/api/gulfexc/offers/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_gulfexc_offer_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [
                ("merchant_id", "!=", False),
                ("merchant_id.active", "!=", False),
                ("is_in_offer", "=", True),
            ]

            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data["merchant_id"]))

            if data.get("merchant_category_id"):
                merchants = (
                    request.env["res.partner"]
                    .sudo()
                    .search(
                        [("partner_category_id", "=", data["merchant_category_id"])]
                    )
                )
                domain.append(("merchant_id", "in", merchants.ids))

            if data.get("x_offer_type"):
                domain.append(("offer_type", "=", data["x_offer_type"]))

            if data.get("x_for_employee_type"):
                domain += [
                    "|",
                    ("employee_type", "=", data["x_for_employee_type"]),
                    ("employee_type", "=", "both"),
                ]

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

            products = (
                request.env["product.template"]
                .sudo()
                .search_read(
                    domain,
                    [
                        "employee_type",
                        "name",
                        "offer_type",
                        "image_url",
                        "list_price",
                        "default_code",
                        "point",
                        "online_store",
                        "max_quantity",
                        "offer_type_discount",
                        "offer_type_promo_code",
                        "merchant_online_store",
                        "buy_link",
                        "barcode",
                        "description",
                        "description_sale",
                        "description_arabic",
                        "offer_label",
                        "merchant_id",
                        "categ_id",
                        "create_date",
                        "start_date",
                        "end_date",
                        "min_quantity",
                        "discount",
                    ],
                    limit=int(data.get("limit") or 100),
                    offset=int(data.get("offset") or 0),
                    order="create_date desc",
                )
            )

            return self._prepare_offer_product_data(products)

        except Exception as e:
            return {"error": _("Something went wrong. Please try again later.")}

    def _prepare_offer_product_data(self, products):
        datas = []
        web_base_url = (
            request.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        )
        base_url = web_base_url.rstrip("/") if web_base_url else ""

        for product in products:
            try:
                product_template = (
                    request.env["product.template"].sudo().browse(product["id"])
                )

                merchant = product.get("merchant_id") or [False, ""]
                merchant_id, merchant_name = merchant[0], merchant[1]

                category = product.get("categ_id") or [False, ""]
                category_id, category_name = category[0], category[1]

                product_data = dict(product)
                product_data.update(
                    {
                        "ribbon": "15% Discount",
                        "merchant_name": merchant_name,
                        "merchant_id": merchant_id,
                        "merchant_rating": 4,
                        "category_id": category_id,
                        "category_name": category_name,
                        "disc_ribbon": product.get("offer_label"),
                        "point": product.get("point"),
                        "product_merchant_is_business_hotel": merchant_id,
                        "merchant_logo": (
                            url_join(
                                base_url,
                                f"/go/api/image/{merchant_id}/image_1920/res.partner",
                            )
                            if base_url and merchant_id
                            else False
                        ),
                    }
                )

                datas.append(product_data)
            except Exception as e:
                _logger.warning(f"Error formatting product {product.get('id')}: {e}")
                continue

        return datas

    # Todo check again with all domain
    @http.route(
        ["/go/api/user/offers/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def get_users_offer_list(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            domain = [
                ("merchant_id", "!=", False),
                ("merchant_id.active", "!=", False),
                ("is_in_offer", "=", True),
            ]

            if data.get("merchant_id"):
                domain.append(("merchant_id", "=", data["merchant_id"]))

            if data.get("merchant_category_id"):
                merchants = (
                    request.env["res.partner"]
                    .sudo()
                    .search(
                        [("partner_category_id", "=", data["merchant_category_id"])]
                    )
                )
                domain.append(("merchant_id", "in", merchants.ids or [0]))

            if data.get("x_offer_type"):
                domain.append(("x_offer_type", "=", data["x_offer_type"]))

            # Exclude products already linked to user's app records
            app_records = (
                request.env["notin.app"]
                .sudo()
                .search([("parent_id", "=", current_user.partner_id.id)])
            )
            if app_records:
                domain.append(("not_linked_ids", "not in", app_records.ids))

            products = (
                request.env["product.template"]
                .sudo()
                .search_read(
                    domain,
                    [
                        "x_for_employee_type",
                        "name",
                        "x_arabic_name",
                        "x_offer_type",
                        "image_url",
                        "lst_price",
                        "default_code",
                        "x_point",
                        "x_online_store",
                        "max_quantity",
                        "x_offer_type_discount",
                        "x_offer_type_promo_code",
                        "x_merchant_online_store",
                        "x_buy_link",
                        "barcode",
                        "description",
                        "description_sale",
                        "x_description_arabic",
                        "offer_label",
                        "merchant_id",
                        "categ_id",
                        "create_date",
                        "start_date",
                        "end_date",
                        "min_quantity",
                        "discount",
                    ],
                    limit=int(data.get("limit") or 3000),
                    offset=int(data.get("offset") or 0),
                    order="create_date desc",
                )
            )

            return self._prepare_offer_product_data(products)

        except Exception as e:
            _logger.exception("Error in get_users_offer_list")
            return {"error": _("Something went wrong. Please try again later.")}

    @http.route(
        ["/go/api/merchant/redeem/v2"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_redeem(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            organisation = partner.parent_id or partner

            track_value = data.get("track_value")
            if not track_value:
                return {"error": _("Merchant PIN Missing")}

            product_id = data.get("product_id")
            if not product_id:
                return {"error": _("Wrong Product ID")}
            product = (
                request.env["product.template"]
                .sudo()
                .search([("id", "=", int(product_id))], limit=1)
            )
            if not product:
                return {"error": _("Invalid Product ID")}

            if product.merchant_id.merchant_pin_new != track_value:
                return {"error": _("Wrong Merchant PIN")}

            limit_records = product.offer_limit_ids.filtered(
                lambda l: l.partner_id.id == organisation.id
            )
            if limit_records:
                now = fields.Datetime.now()
                frequency_map = {
                    "weekly": lambda: now - timedelta(days=7),
                    "monthly": lambda: now - relativedelta(months=1),
                    "yearly": lambda: now - relativedelta(years=1),
                }

                for limit in limit_records:
                    start_date_func = frequency_map.get(limit.frequency)
                    if not start_date_func:
                        continue

                    start_date = start_date_func()
                    usage_count = (
                        request.env["offer.usages.history"]
                        .sudo()
                        .search_count(
                            [
                                ("partner_id", "=", partner.id),
                                ("product_id", "=", product.id),
                                ("used_on", ">=", start_date),
                            ]
                        )
                    )
                    if usage_count >= limit.number_of_usages:
                        return {
                            "error": _(
                                "You have already consumed your offer limit for this product."
                            )
                        }

            request.env["offer.usages.history"].sudo().create(
                {
                    "partner_id": partner.id,
                    "organisation_id": organisation.id,
                    "product_id": product.id,
                    "usage_count": 1,
                }
            )

            return {"success": True}

        except Exception as e:
            return {"error": _("Something went wrong. Please try again later.")}

    @http.route(
        ["/go/api/merchant/dashboard/data"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
    )
    def get_merchant_details(self, **post):
        try:
            data = post or self._get_json_request()
            if "error" in data:
                return data

            current_user = self._validate_token(data)
            if isinstance(current_user, dict):
                return current_user

            partner = current_user.partner_id
            if partner.entity_type != "merchant":
                return {"error": _("You are not allowed to access this API")}

            web_base_url = (
                request.env["ir.config_parameter"].sudo().get_param("web.base.url")
            )
            return self._get_merchant_profile(partner, web_base_url)

        except Exception as e:
            return {"error": _("Something went wrong: %s") % str(e)}

    def _get_merchant_profile(self, partner, web_base_url):
        products = self._get_products(partner)
        category = partner.partner_category_id

        return {
            "id": partner.id,
            "merchant_name": partner.name,
            "phone": partner.phone,
            "email": partner.email or "",
            "address": partner.contact_address,
            "partner_latitude": partner.partner_latitude,
            "partner_longitude": partner.partner_longitude,
            "description": partner.merchant_details_en,
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
            "available_points": partner.points,
            "points_used": partner.points_used,
            "points_earn": partner.points_earn,
            "banners": self._get_banners(partner, web_base_url),
            "total_products": len(products),
            "products": products,
            "offer_products": self._get_offer_products(partner),
            "transactions": self._get_transactions(partner),
            "total_sales": self._get_total_sales(partner),
            "top_5_customers": self._get_top_5_customers(partner, web_base_url),
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

    def _get_top_5_customers(self, partner, web_base_url):
        datas = (
            request.env["loyalty.sale"]
            .sudo()
            .read_group(
                [("merchant_id", "=", partner.id)],
                ["partner_id", "amount"],
                ["partner_id", "amount"],
                limit=5,
                orderby="amount desc",
            )
        )
        Partner = request.env["res.partner"].sudo()
        res = []
        for d in datas:
            partner = Partner.browse(d["partner_id"][0])
            res.append(
                {
                    "sales": d["amount"],
                    "customer": partner.name,
                    "phone": partner.phone,
                    "email": partner.email,
                    "logo": partner.image_url,
                }
            )
        return res

    def _get_banners(self, partner, web_base_url):
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
                web_base_url, f"/go/api/image/{banner['id']}/image_1920/merchant.banner"
            )
        return banners

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

    def _get_transactions(self, partner):
        fields = ["name", "amount", "date", "partner_id"]
        return (
            request.env["loyalty.sale"]
            .sudo()
            .search_read([("merchant_id", "=", partner.id)], fields, limit=20)
        )

    def _get_total_sales(self, partner):
        return sum(
            request.env["loyalty.sale"]
            .sudo()
            .search([("merchant_id", "=", partner.id)])
            .mapped("amount")
        )
