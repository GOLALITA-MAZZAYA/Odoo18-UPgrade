# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductTags(models.Model):
    _name = "product.tags"
    _description = "Product Tag"
    _order = "sequence, id"

    _sql_constraints = [
        ('unique_tag_name', 'unique (name)', "A tag with this name already exists!")
    ]



    name = fields.Char(
        string="Tag Name",
        required=True,
        translate=True,
        help="The display name of the tag."
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        help="Enable or disable this tag without deleting it."
    )

    sequence = fields.Integer(
        string="Sequence",
        help="Defines the order of tags when displayed in lists."
    )

    product_ids = fields.Many2many(
        'product.template',
        string='Associated Products',
        help="Products that are linked with this tag."
    )


