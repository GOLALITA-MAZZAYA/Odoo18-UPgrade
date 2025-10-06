from odoo import models, fields, api, _


class LoyaltyNotificationList(models.Model):
    _name = "loyalty.notification.list"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Notification List"

    partner_id = fields.Many2one("res.partner", string="Customer", tracking=True)
    merchant_id = fields.Many2one("res.partner", string="Merchant", tracking=True)
    description = fields.Text(string="Description")
    date = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        tracking=True,
    )
    notification_type = fields.Selection(
        [
            ("transfer", "Transfer"),
            ("sale_reward", "Sales Reward"),
            ("sale_redeem", "Sale Redeem"),
            ("offer", "Offer"),
            ("product", "Product"),
        ],
        string="Notification Type",
        tracking=True
    )
    state = fields.Selection(
        [("unread", "Unread"), ("read", "Read")],
        tracking=True,
        string="Status",
        default="unread",
    )

    url = fields.Char(string="Notification URL")
    product_id = fields.Many2one("product.template", string="Product")
    offer_image = fields.Binary(string="Offer Image")

    @api.depends("notification_type", "partner_id", "date")
    def _compute_display_name(self):
        for record in self:
            record.display_name = (
                f"{record.notification_type or ''} - "
                f"{record.partner_id.name or ''} - "
                f"{record.date.strftime('%Y-%m-%d') if record.date else ''}"
            )
