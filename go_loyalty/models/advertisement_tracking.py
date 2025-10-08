from odoo import models, fields


class AdvertisementTracking(models.Model):
    _name = "advertisement.tracking"
    _description = "Advertisement Tracking"
    _rec_name = "tracking_code"

    partner_id = fields.Many2one("res.partner", string="Customer")
    customer_name = fields.Char(
        string="Customer Name",
    )
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    tracking_code = fields.Char(
        string="Tracking Code",
        required=True,
        index=True,
        help="Unique tracking code for advertisement",
    )

    date = fields.Datetime(
        string="Tracking Date",
        default=fields.Datetime.now,
        help="Date and time of tracking",
    )
