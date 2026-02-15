from odoo import models, fields, api,_
import base64
import uuid
from odoo.exceptions import ValidationError
from openai import OpenAI


from odoo.addons.go_giftcard.models.ugo2gift_api_request import Ugo2GiftAPI


class SubscriptionHistory(models.Model):
    _name = "subscription.history"
    _description = "Subscription History"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date desc"

    # Core Info
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        help="The customer linked to this subscription.",
    )
    plan_id = fields.Many2one(
        "subscription.plan",
        string="Subscription Plan",
        required=True,
        help="The subscription plan purchased by the customer.",
    )
    subscription_reference = fields.Char(
        string="Subscription Reference",
        readonly=True,
        copy=False,
        help="A unique reference code for this subscription history record.",
    )
    price = fields.Float(
        string="Plan Price",
        related="plan_id.price",
        store=True,
        help="The price of the subscription plan.",
    )

    # Date Management
    start_date = fields.Date(
        string="Start Date", help="The date when this subscription becomes active."
    )
    end_date = fields.Date(
        string="End Date", help="The date when this subscription ends."
    )
    is_active = fields.Boolean(
        compute="_compute_is_active",
        store=True,
        string="Currently Active",
        help="Indicates whether the subscription is currently active based on "
        "its start/end dates and payment status.",
    )

    # Payment Tracking
    payment_reference = fields.Char(
        string="Payment Reference",
        help="The reference identifier for the payment linked to this subscription.",
    )
    payment_web_link = fields.Char(
        string="Payment URL",
        help="The external payment link or URL for this subscription's payment.",
    )
    payment_state = fields.Selection(
        [("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed")],
        default="pending",
        string="Payment Status",
        tracking=True,
        help="The current status of the payment for this subscription.",
    )

    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["subscription_reference"] = f"S-{uuid.uuid4().hex[:10].upper()}"
            start_date = vals.get("start_date")
            end_date = vals.get("end_date")
            partner_id = vals.get("partner_id")
            if start_date and end_date and partner_id:
                self._validate_overlap(partner_id, start_date, end_date)
        return super().create(vals_list)

    def _validate_overlap(self, partner_id, start_date, end_date):
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)

        overlapping = self.search(
            [
                ("partner_id", "=", partner_id),
                ("is_active", "=", True),
                ("start_date", "<=", end_date),
                ("end_date", ">=", start_date),
            ],
            limit=1,
        )

        if overlapping:
            raise ValidationError(
                _(
                    "An active subscription already exists for this customer "
                    "overlapping the selected date range."
                )
            )

    @api.depends("start_date", "end_date", "payment_state")
    def _compute_is_active(self):
        today = fields.Date.today()
        for rec in self:
            rec.is_active = (
                rec.payment_state == "paid"
                and rec.start_date
                and rec.end_date
                and rec.start_date <= today <= rec.end_date
            )

    @api.depends("partner_id", "plan_id", "partner_id.name", "plan_id.name", "start_date", "end_date")
    def _compute_display_name(self):
        for rec in self:
            customer = rec.partner_id.name or "Unknown"
            plan = rec.plan_id.name or "No Plan"
            period = (
                f"{rec.start_date}→{rec.end_date}"
                if rec.start_date and rec.end_date
                else "No Dates"
            )
            rec.display_name = f"{customer} - {plan} [{period}]"

    def get_skipcash_url(
        self,
        transaction_id,
        current_user,
    ):
        api_url, merchant_key, merchant_password = (
            self.env["gift.card"]._check_skipcash_api_credentials()
        )

        uid = str(uuid.uuid4())

        amount = round(self.plan_id.price, 2)

        payload = {
            "Uid": uid,
            "KeyId": merchant_key,
            "Amount": str(amount),
            "FirstName": current_user.partner_id.name,
            "LastName": current_user.partner_id.name,
            "Email": current_user.partner_id.email,
            "TransactionId": transaction_id,
        }

        signing_string = ",".join(f"{k}={v}" for k, v in payload.items())
        signature = self.env["gift.card"].hash_hmac(signing_string, merchant_password, raw_output=True)
        authorization = base64.b64encode(signature).decode("utf-8")
        payload["ReturnUrl"] = "golalita://subscriptions"

        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }

        skipcash_api = Ugo2GiftAPI(
            self.env, api_url, merchant_key, merchant_password, headers=headers
        )

        response = skipcash_api.create_skipcash_payment(payload)

        if response.get("success"):
            result_obj = response.get("data", {}).get("resultObj", {})
            return {
                "id": result_obj.get("id"),
                "pay_url": result_obj.get("payUrl"),
            }

        return {"error": response.get("message", "Failed to create Skipcash payment")}
