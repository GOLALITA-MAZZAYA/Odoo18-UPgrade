import uuid
from odoo import http, fields, _
from odoo.http import request
from datetime import timedelta
from odoo.exceptions import ValidationError
import json


class SubscriptionController(http.Controller):

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

    def _create_subscription(
        self, user, plan, payment_reference=False, payment_state="pending", is_active=False
    ):
        today = fields.Date.today()
        end_date = today + timedelta(days=plan.duration_days)

        return (
            request.env["subscription.history"]
            .sudo()
            .create(
                {
                    "partner_id": user.partner_id.id,
                    "plan_id": plan.id,
                    "payment_reference": payment_reference,
                    "start_date": today,
                    "end_date": end_date,
                    "payment_state": payment_state,
                    "is_active": is_active,
                }
            )
        )

    @http.route(
        ["/subscription/payment/request"],
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
        type="json",
        cors="*",
    )
    def create_subscription_payment_request(self, **post):
        # Parse data and validate user
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        plan_id = data.get("plan_id")
        return_url = data.get("return_url")
        if not plan_id or not return_url:
            return {"error": _("Missing required fields: plan_id, return_url")}

        plan = request.env["subscription.plan"].sudo().browse(int(plan_id))
        if not plan.exists():
            return {"error": _("Invalid subscription plan.")}

        payment_reference = str(uuid.uuid4())
        try:
            subscription = self._create_subscription(
                user=user,
                plan=plan,
                payment_reference=payment_reference,
                payment_state="pending",
                is_active=False,
            )
        except ValidationError as e:
            return {"error": str(e)}

        payment_data = subscription.get_skipcash_url(
            transaction_id=payment_reference, current_user=user
        )
        if not payment_data:
            return {"error": _("Failed to generate payment link.")}

        subscription.write(
            {
                "payment_web_link": payment_data.get("pay_url"),
                "payment_state": "pending",
            }
        )

        return {
            "subscription_id": subscription.id,
            "subscription_reference": subscription.subscription_reference,
            "payment_reference": subscription.payment_reference,
            "payment_web_link": subscription.payment_web_link,
            "price": subscription.price,
            "state": subscription.payment_state,
        }

    @http.route(
        ["/subscription/redeem/code"],
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def redeem_subscription_code(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        code = data.get("code")

        if not code:
            return {"error": _("Code are required.")}

        today = fields.Date.today()
        code = (
            request.env["subscription.code"]
            .sudo()
            .search(
                [
                    ("name", "=", code),
                    ("expiry_date", ">=", today),
                    ("is_redeemed", "=", False),
                ],
                limit=1,
            )
        )
        if not code:
            return {"error": _("Invalid or expired code.")}

        try:
            subscription = self._create_subscription(
                user=user,
                plan=code.plan_id,
                payment_reference=f"CODE-{code.name}",
                payment_state="paid",
                is_active=True,
            )
        except ValidationError as e:
            return {"error": str(e)}

        code.write(
            {
                "is_redeemed": True,
                "redeemed_by": user.id,
                "redeemed_on": fields.Datetime.now(),
            }
        )

        return {
            "message": _("Subscription activated via code."),
            "subscription_id": subscription.id,
            "subscription_reference": subscription.subscription_reference,
            "start_date": str(subscription.start_date),
            "end_date": str(subscription.end_date),
            "plan": subscription.plan_id.name,
        }


    @http.route(
        "/go/api/user/subscription/plans",
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
    )
    def get_all_plans(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        plans = request.env["subscription.plan"].sudo().search([])
        result = [
            {
                "id": plan.id,
                "name": plan.name,
                "arabic_name": plan.arabic_name,
                "code": plan.code,
                "duration_days": plan.duration_days,
                "price": plan.price,
                "description": plan.description or "",
                "arabic_description": plan.arabic_description or "",
            }
            for plan in plans
        ]
        return {"plans": result}

    @http.route(
        "/go/api/user/subscription/subscribe",
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def subscribe_user_to_plan(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        plan_id = data.get("plan_id")
        if not plan_id:
            return {"error": _("Plan ID is required.")}

        plan = request.env["subscription.plan"].sudo().browse(int(plan_id))
        if not plan.exists():
            return {"error": _("Invalid subscription plan.")}

        subscription = self._create_subscription(
            user=user,
            plan=plan,
            payment_state="paid",
        )

        return {
            "message": _("User subscribed successfully."),
            "subscription_id": subscription.id,
            "plan": plan.name,
            "start_date": str(subscription.start_date),
            "end_date": str(subscription.end_date),
        }

    @http.route(
        "/go/api/user/subscription/status",
        auth="public",
        type="json",
        methods=["POST"],
        csrf=False,
        cors="*",
    )
    def get_subscription_status(self, **post):
        data = post or self._get_json_request()
        if "error" in data:
            return data

        user = self._validate_token(data)
        if isinstance(user, dict) and "error" in user:
            return user

        today = fields.Date.today()
        history = (
            request.env["subscription.history"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", user.partner_id.id),
                    ("start_date", "<=", today),
                    ("end_date", ">=", today),
                    ("payment_state", "=", "paid"),
                    ("is_active", "=", True),
                ],
                order="start_date desc",
                limit=1,
            )
        )

        if not history:
            return {
                "message": _("No active subscription found."),
                "subscription_status": "inactive",
                "payment_status": "none",
            }

        plan = history.plan_id
        return {
            "message": _("Active subscription found."),
            "subscription_status": "active",
            "subscription_reference": history.subscription_reference,
            "payment_status": history.payment_state,
            "plan": plan.name,
            "code": plan.code,
            "start_date": str(history.start_date),
            "end_date": str(history.end_date),
            "days_left": (history.end_date - today).days,
        }
