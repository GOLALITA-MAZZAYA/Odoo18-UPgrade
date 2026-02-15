from odoo import models, fields, _


class LoyaltyContactUs(models.Model):
    _name = "loyalty.contact.us"
    _description = "Contact Us"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner", string="Partner")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    note = fields.Text(string="Query / Notes")
    date = fields.Datetime(string="Date", default=fields.Datetime.now)
    # priority = fields.Integer(string="Rating", default=0)

    imp_notification = fields.Boolean(string="Important Notification")
    description = fields.Html(string="Description")
