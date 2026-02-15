from odoo import fields, models


class MultiOffers(models.Model):
    _name = "multi.offers"
    _description = "Multiple Promotional Offers"

    offer_type = fields.Selection(
        [
            ("b1g1", "Buy One Get One"),
            ("discount", "Discount"),
            ("promocode", "Promocode"),
        ],
        string="Offer Type",
        help="Select the type of promotional offer:\n"
        "- Buy One Get One: Customer receives an extra item free.\n"
        "- Discount: A fixed percentage or amount off the price.\n"
        "- Promocode: A code customers can use to apply the offer.",
    )

    discount = fields.Float(
        string="Discount (%)",
        help="Enter the discount percentage for the offer.\n"
        "Example: 10 means a 10% discount.",
    )

    promocode = fields.Char(
        string="Promocode",
        help="Specify a promocode that customers must enter to avail the offer.",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Organisation",
        help="Select the organisation or customer for whom this offer is valid.",
    )

    product_id = fields.Many2one(
        "product.template",
        string="Product",
        help="Select the product to which this offer applies.",
    )
