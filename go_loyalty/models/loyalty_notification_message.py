from odoo import models, fields, _


class LoyaltyNotificationMessage(models.Model):
    _name = "loyalty.notification.message"
    _description = "Loyalty Notification Message"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "subject"

    message = fields.Text(string="Message Content")

    message_arabic = fields.Text(string="Message Content (Arabic)")

    notification_id = fields.Many2one(
        "loyalty.notification",
        string="Notification",
    )

    state = fields.Selection(
        [("pending", "Pending"), ("sent", "Sent")],
        string="Message Status",
        default="pending",
        tracking=True,
    )

    description = fields.Html(string="Description")

    description_arabic = fields.Html(string="Description (Arabic)")

    imp_notification = fields.Boolean(string="Important Notification")

    merchant_id = fields.Many2one(
        "res.partner", domain=[("entity_type", "=", "merchant")], string="Merchant"
    )

    offer_image = fields.Binary(string="Offer Image")

    org_id = fields.Many2one(
        "res.partner",
        string="Organisation",
        domain=[("entity_type", "=", "organisation")],
    )

    product_id = fields.Many2one("product.template", string="Product")

    subject = fields.Char(string="Subject")

    subject_arabic = fields.Char(string="Subject (Arabic)")

    url = fields.Char(string="Redirect URL")
