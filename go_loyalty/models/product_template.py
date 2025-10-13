# -*- coding: utf-8 -*-
from odoo import fields, models


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



