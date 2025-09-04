from odoo import api, fields, models
from odoo.tools.translate import html_translate


class ProductBrand(models.Model):
    _name = "product.brand"
    _inherit = ["website.multi.mixin", "mail.thread.cc", "mail.activity.mixin"]
    _description = "Product Brand"
    _order = "sequence,id"

    sequence = fields.Integer(
        string="Sequence", help="Defines the display order of the brand."
    )

    name = fields.Char(
        string="Brand Name",
        translate=True,
        required=True,
        help="The name of the brand.",
    )

    logo = fields.Binary(
        string="Brand Logo", required=True, help="Upload the logo for this brand."
    )

    visible_slider = fields.Boolean(
        string="Show on Website",
        default=True,
        help="Enable to display this brand in website sliders or listings.",
    )

    active = fields.Boolean(
        string="Active", default=True, help="Uncheck to archive this brand."
    )

    brand_description = fields.Text(
        string="Internal Notes",
        translate=True,
        help="Internal description of the brand (not shown on website).",
    )

    description = fields.Html(
        string="Website Description",
        translate=html_translate,
        help="Description shown on the website for this brand.",
    )

    brand_product_ids = fields.One2many(
        "product.template",
        "brand_id",
        string="Products",
        help="Products associated with this brand.",
    )

    products_count = fields.Integer(
        string="Number of Products",
        compute="_get_products_count",
        help="Total number of products linked to this brand.",
    )

    @api.depends("brand_product_ids")
    def _get_products_count(self):
        for rec in self:
            rec.products_count = len(rec.brand_product_ids)
