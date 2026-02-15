from odoo import fields, models


class FavouriteProduct(models.Model):
    _name = "favourite.product"
    _description = "Favourite Product"

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        help="The customer who marked this product as favorite.",
    )

    is_voucher = fields.Boolean(
        string="Voucher Applied",
        help="Indicates if the favorite is linked with a voucher.",
    )

    is_save = fields.Boolean(
        string="Saved for Later",
        help="Indicates if the customer saved this product for later.",
    )

    product_id = fields.Many2one(
        "product.template",
        string="Product",
        help="The product that has been favorited by the customer.",
    )
