from odoo import models, fields


class SubscriptionCode(models.Model):
    _name = 'subscription.code'
    _description = 'Subscription Access Code'

    name = fields.Char(
        string="Access Code",
        required=True,
        help="A unique code that provides access to a subscription plan."
    )

    plan_id = fields.Many2one(
        'subscription.plan',
        string="Subscription Plan",
        required=True,
        help="The subscription plan this access code belongs to."
    )

    merchant_id = fields.Many2one(
        'res.partner',
        string="Merchant",
        help="The merchant or business partner who issued this access code."
    )

    expiry_date = fields.Date(
        string="Code Expiry",
        required=True,
        help="The date after which this access code can no longer be used."
    )

    is_redeemed = fields.Boolean(
        string="Redeemed",
        default=False,
        help="Indicates whether this access code has been used."
    )

    redeemed_by = fields.Many2one(
        'res.users',
        string="Redeemed By",
        readonly=True,
        help="The user who redeemed this access code."
    )

    redeemed_on = fields.Datetime(
        string="Redeemed On",
        readonly=True,
        help="The date and time when the access code was redeemed."
    )
