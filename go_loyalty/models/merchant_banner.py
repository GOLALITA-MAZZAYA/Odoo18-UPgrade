from odoo import models, fields


class MerchantBanner(models.Model):
    _name = "merchant.banner"
    _description = "Merchant Banner"
    _order = "create_date desc"

    name = fields.Char(string="Banner Name")
    image_1920 = fields.Image(string="Banner Image", required=True)
    partner_id = fields.Many2one(
        "res.partner",
    )

    merchant_rating = fields.Selection(
        related="partner_id.merchant_rating",
        string="Merchant Rating",
        store=True,
    )

    sequence = fields.Integer(string="Sequence")
