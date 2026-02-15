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
        return any(
            (l.partner_id.id == partner_id and l.is_subscribe) for l in self.line_ids
        )

    def _subscribe_user(self, partner, device_id):
        self.ensure_one()
        line = self.line_ids.filtered(lambda l: l.partner_id.id == partner.id)
        if line:
            line.write(
                {
                    "device_id": device_id,
                    "is_subscribe": True,
                }
            )
        else:
            self.env["loyalty.notification.line"].sudo().create(
                {
                    "notification_id": self.id,
                    "partner_id": partner.id,
                    "device_id": device_id,
                    "is_subscribe": True,
                }
            )

    def _unsubscribe_user(self, partner):
        self.ensure_one()
        line = self.line_ids.filtered(lambda l: l.partner_id.id == partner.id)
        if line:
            line.write({"is_subscribe": False})

    @api.depends("merchant_id", "line_ids")
    def _compute_display_name(self):
        for rec in self:
            merchant_name = rec.merchant_id.name if rec.merchant_id else "No Merchant"
            subscribers_count = sum(1 for l in rec.line_ids if l.is_subscribe)
            rec.display_name = f"{merchant_name} ({subscribers_count} subscribers)"
