from odoo import models, fields, api


class SubscriptionHistory(models.Model):
    _name = "subscription.history"
    _description = "Subscription History"
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
        help="The current status of the payment for this subscription.",
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
