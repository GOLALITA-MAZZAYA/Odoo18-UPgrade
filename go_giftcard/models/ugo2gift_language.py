from odoo import models, fields


class Ugo2GiftLanguage(models.Model):
    _name = "ugo2gift.language"
    _description = "Ugo2Gift Language"

    name = fields.Char(
        string="Language Name",
        required=True,
        help="Enter the name of the language (e.g., English, Arabic).",
    )

    lang_code = fields.Char(
        string="Language Code",
        required=True,
        help="Enter the ISO code of the language (e.g., en, ar).",
    )

    country_id = fields.Many2one(
        "ugo2gift.country",
        string="Country",
        help="Select the country to which this language belongs.",
    )
