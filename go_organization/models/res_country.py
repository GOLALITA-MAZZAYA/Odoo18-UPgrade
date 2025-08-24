from odoo import models, fields


class ResCountry(models.Model):
    _inherit = "res.country"

    name_ar = fields.Char(string="Name (Arabic)", help="Localized Arabic name.")
