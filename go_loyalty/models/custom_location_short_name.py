from odoo import fields, models

class LocationShortName(models.Model):
    _name = 'custom.location.short.name'
    _description = 'Location Short Name'

    name = fields.Char(string='Short Name', required=True)