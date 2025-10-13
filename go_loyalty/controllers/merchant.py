from odoo import http, fields, _
from odoo.http import request
from werkzeug.urls import url_join
from datetime import timedelta,datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
import json

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
                "discount": sale.discount
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
                    [("id", "=", data["merchant_id"]), ("entity_type", "=", "merchant")],
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

