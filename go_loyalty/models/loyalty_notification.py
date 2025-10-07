from odoo import models, fields, api, _


class LoyaltyNotification(models.Model):
    _name = "loyalty.notification"
    _description = "Loyalty Notification"
    _rec_name = "merchant_id"

    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        required=True,
        domain=[("entity_type", "=", "merchant")],
    )

    line_ids = fields.One2many(
        "loyalty.notification.line",
        "notification_id",
    )


