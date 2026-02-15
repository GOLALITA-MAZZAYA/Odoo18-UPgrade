from odoo import fields, models


class OfferLimits(models.Model):
    _name = "offer.limits"
    _description = "Offer Usage Limits"

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)

    frequency = fields.Selection(
        [("weekly", "Weekly"), ("monthly", "Monthly"), ("yearly", "Yearly")],
        string="Frequency",
        required=True,
    )

    number_of_usages = fields.Integer(string="Maximum Usages", required=True)

    product_id = fields.Many2one(
        "product.template", string="Product", ondelete="cascade"
    )
