from odoo import models, fields, api


class SubscriptionPlan(models.Model):
    _name = 'subscription.plan'
    _description = 'Subscription Plan'

    name = fields.Char(
        string="Plan Name",
        required=True,
        help="The name of the subscription plan in English."
    )
    arabic_name = fields.Char(
        string="Plan Name (Arabic)",
        help="The name of the subscription plan in Arabic."
    )
    code = fields.Char(
        string="Plan Code",
        required=True,
        help="A unique internal code to identify this subscription plan."
    )
    duration_days = fields.Integer(
        string="Duration (Days)",
        required=True,
        help="The number of days this subscription plan will remain valid."
    )
    price = fields.Float(
        string="Price (QAR)",
        required=True,
        help="The price of the subscription plan in Qatari Riyals (QAR)."
    )
    description = fields.Text(
        string="Description",
        help="A detailed description of the subscription plan in English."
    )
    arabic_description = fields.Text(
        string="Description (Arabic)",
        help="A detailed description of the subscription plan in Arabic."
    )
    subscription_code_ids = fields.One2many(
        'subscription.code',
        'plan_id',
        string="Subscription Codes",
        help="List of unique subscription codes generated for this plan."
    )
    active_user_ids = fields.One2many(
        'subscription.history',
        'plan_id',
        string="Active Subscribers",
        domain=[('is_active', '=', True)],
        help="All active subscriptions currently linked to this plan."
    )

