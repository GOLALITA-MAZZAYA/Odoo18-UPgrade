# -*- coding: utf-8 -*-
from odoo import fields, models,api
from urllib.parse import urljoin

class ProductTemplate(models.Model):
    _inherit = "product.template"

    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain="[('entity_type', '=', 'merchant')]",
    )

    is_in_offer = fields.Boolean(
        string="Included in Offer",
        help="Indicates if the product is part of an active offer.",
    )

    offer_type = fields.Selection(
        [
            ('b1g1','B1G1'),
            ('discount','Discount'),
            ('promocode','Promocode'),
            ('giftcard','Gift Card'),
        ],
        oldname="x_offer_type"
    )

    employee_type = fields.Selection(
        selection=[
            ("vip", "VIP"),
            ("standard", "Standard"),
            ("both", "Both"),
        ],
        string="Employee Type",
        help="Select whether the employee is VIP, Standard, or Both.",
        oldname="x_for_employee_type",
    )

    image_url = fields.Char(compute="_compute_image_url", store=False)

    point = fields.Float(oldname="x_point")
    online_store = fields.Float(oldname="x_online_store")
    min_quantity = fields.Float(string="Minimum Purchase QTY")
    max_quantity = fields.Float(string="Maximum Purchase QTY")
    offer_type_discount = fields.Float(oldname="x_offer_type_discount")
    offer_type_promo_code = fields.Char(oldname="x_offer_type_promo_code")
    merchant_online_store = fields.Char(oldname="x_merchant_online_store")
    buy_link = fields.Char(oldname="x_buy_link")
    description_arabic = fields.Text(oldname="x_description_arabic")
    offer_label = fields.Char()
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    discount = fields.Float(string="Flat Discount")
    offer_limit_ids = fields.One2many('offer.limits', 'product_id', string='Offer Limits')
    arabic_name = fields.Char(string="Arabic Name", oldname="x_arabic_name")

    offer_copy = fields.Binary(string='Offer Copy',oldname="x_offer_copy", attachment=True)
    offer_copy_name = fields.Char(string='Offer Copy Name',oldname="x_offer_copy_name")
    favourite_partner_ids = fields.One2many(
        "favourite.product", "product_id", string="Favourite Partners"
    )

    label_arabic = fields.Char(string="Arabic Label", oldname="x_label_arabic")

    @api.depends('image_512')
    def _compute_image_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if not base_url:
            for product in self:
                product.image_url = False
            return

        base_url = base_url.rstrip("/")
        for product in self:
            product.image_url = (
                urljoin(
                    base_url, f"/go/api/image/{product.id}/image_512/product.template"
                )
                if product.id
                else False
            )
