from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductSticker(models.Model):
    _name = "product.sticker"
    _description = "Product Sticker"
    _order = "sequence, name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Basics
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, index=True)
    sequence = fields.Integer(default=10)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        readonly=True,
    )

    # Behavior
    sticker_type = fields.Selection(
        [
            ("html", "Text/HTML"),
            ("image", "Image"),
        ],
        required=True,
        default="html",
        tracking=True,
        help="Choose whether this sticker is rendered from styled text/HTML or from a static image.",
    )

    position = fields.Selection(
        [
            ("top_left", "Top Left"),
            ("top_right", "Top Right"),
            ("bottom_left", "Bottom Left"),
            ("bottom_right", "Bottom Right"),
        ],
        required=True,
        default="top_right",
        help="Anchor position where the sticker will be placed on the product image/card.",
    )

    # Text/HTML mode
    sticker_text = fields.Text(
        help="Sticker text"
    )
    font_size = fields.Integer(
        string="Font Size (px)",
        help="Font size in pixels for HTML sticker.",
    )
    # Use hex colors with widget=color (e.g., #FF0000)
    bg_color = fields.Char(string="Background Color (Hex)", help="Example: #FF0000")
    text_color = fields.Char(string="Text Color (Hex)", help="Example: #FFFFFF")

    shape = fields.Selection(
        [
            ("rectangle", "Rectangle"),
            ("square", "Square"),
            ("circle", "Circle"),
        ],
        default="circle",
        help="Visual style of the HTML sticker.",
    )
    rotate = fields.Integer(
        string="Rotate (deg)",
        default=0,
        help="Rotation in degrees (0–360).",
    )
    cut_corner = fields.Boolean(
        string="Cut Corner",
        help="Applies a clipped corner style where supported by your renderer.",
    )

    # Image mode
    image = fields.Image(
        max_width=1920,
        max_height=1920,
        attachment=True,
        help="Image used when sticker type is Image.",
    )

    # Layout / geometry (common)
    width = fields.Float(help="Sticker width in pixels.")
    height = fields.Float(help="Sticker height in pixels.")
    top = fields.Float(help="Top offset in pixels from the anchor.")
    bottom = fields.Float(help="Bottom offset in pixels from the anchor.")
    left = fields.Float(help="Left offset in pixels from the anchor.")
    right = fields.Float(help="Right offset in pixels from the anchor.")

    # ─────────────────────────────────────────────────────────────────────
    # CONSTRAINTS (server-side safety)
    # ─────────────────────────────────────────────────────────────────────
    @api.constrains("rotate")
    def _check_rotate_range(self):
        for rec in self:
            if rec.rotate is not None and (rec.rotate < 0 or rec.rotate > 360):
                raise ValidationError(_("Rotate must be between 0 and 360 degrees."))

    @api.constrains("width", "height", "top", "bottom", "left", "right", "font_size")
    def _check_dimensions_positive(self):
        for rec in self:
            for fname in ("width", "height", "font_size"):
                val = rec[fname]
                if val is not None and val < 0:
                    raise ValidationError(_("%s cannot be negative.") % dict(self._fields)[fname].string)

    @api.constrains("bg_color", "text_color")
    def _check_hex_colors(self):
        import re
        hex_pat = re.compile(r"^#([0-9A-Fa-f]{6})$")
        for rec in self:
            for color_f in ("bg_color", "text_color"):
                c = rec[color_f]
                if c and not hex_pat.match(c):
                    raise ValidationError(_("Invalid %s. Use hex like #RRGGBB.") % dict(self._fields)[color_f].string)