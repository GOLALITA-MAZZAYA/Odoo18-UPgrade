from odoo import models, fields


class Ugo2GiftCategory(models.Model):
    _name = "ugo2gift.category"
    _description = "UGO2GIFT Category"

    name = fields.Char(
        string="Category Name",
        required=True,
        help="The display name of the gift card category.",
    )

    category_id = fields.Integer(string="Category ID")

    brand_url = fields.Char(
        string="Brand URL",
        oldname="brands_url",
        help="The API or external URL where brand details for this category can be accessed.",
    )

    image = fields.Binary(
        string="Category Image",
        attachment=True,
        help="Upload an image representing this category (e.g., icon or banner).",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )
