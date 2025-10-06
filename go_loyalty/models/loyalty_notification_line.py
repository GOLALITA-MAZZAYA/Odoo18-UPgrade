from odoo import models, fields, _


class LoyaltyNotificationLine(models.Model):
    _name = "loyalty.notification.line"
    _description = "Loyalty Notification Line"

    notification_id = fields.Many2one("loyalty.notification", ondelete="cascade")

    partner_id = fields.Many2one("res.partner", string="Partner")

    device_id = fields.Char(
        string="Device ID",
    )

    is_subscribe = fields.Boolean(string="Subscribed")
