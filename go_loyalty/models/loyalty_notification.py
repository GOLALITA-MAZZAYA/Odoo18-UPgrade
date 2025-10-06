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

    def _is_subscribed(self, partner_id):
        self.ensure_one()
        return (
            self.line_ids.filtered(
                lambda l: l.partner_id.id == partner_id and l.is_subscribe
            )
            and True
            or False
        )

    def _subscribe_user(self, partner, device_id):
        self.ensure_one()
        existing_line = self.line_ids.filtered(lambda l: l.partner_id == partner)

        if existing_line:
            existing_line.write({"device_id": device_id, "is_subscribe": True})
        else:
            self.env["loyalty.notification.line"].create(
                {
                    "notification_id": self.id,
                    "partner_id": partner.id,
                    "device_id": device_id,
                    "is_subscribe": True,
                }
            )

    def _unsubscribe_user(self, partner):
        self.ensure_one()
        self.line_ids.filtered(lambda l: l.partner_id == partner).write(
            {"is_subscribe": False}
        )
