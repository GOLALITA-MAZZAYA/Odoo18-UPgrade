from odoo import models, fields, api


class Ugo2GiftImage(models.Model):
    _name = "ugo2gift.image"
    _description = "UGO2GIFT Brand Image"

    brand_id = fields.Many2one(
        "ugo2gift.brand",
        string="Brand",
        help="Select the brand associated with this image.",
        ondelete="cascade",
    )

    image_url = fields.Char(
        string="Image URL",
        oldname="image",
        help="Enter the full URL where the image is stored.",
    )

    @api.depends("brand_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.brand_id.name or 'No Brand'}"
