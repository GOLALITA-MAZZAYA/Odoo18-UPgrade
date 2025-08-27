# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductLabelLine(models.Model):
    _name = 'product.label.line'
    _description = 'Product Label Line'

    _sql_constraints = [
        (
            'unique_product_website_label',
            'unique (product_tmpl_id, website_id)',
            'A label line already exists for this product on the selected website.'
        )
    ]

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product',
        required=True,
        help="The product to which this label is applied."
    )

    website_id = fields.Many2one(
        'website',
        string='Website',
        required=True,
        help="Website where this label will be visible. "
             "Useful when you manage multiple websites."
    )

    label = fields.Many2one(
        'product.label',
        string='Label',
        required=True,
        help="The label to display with this product "
             "(e.g. New, Bestseller, Limited Offer)."
    )
