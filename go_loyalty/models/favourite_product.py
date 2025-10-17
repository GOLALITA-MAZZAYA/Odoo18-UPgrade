from odoo import models, fields, api


class FavouriteProduct(models.Model):
    _name = "favourite.product"
    _description = "Favourite Product"

    partner_id = fields.Many2one("res.partner")
    is_voucher = fields.Boolean(string="Is Voucher")
    is_save = fields.Boolean(string="Is Save")
    product_id = fields.Many2one("product.template")
    fav_merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain="[('entity_type', '=', 'merchant')]",
        oldname="x_fav_merchant_id"
    )
