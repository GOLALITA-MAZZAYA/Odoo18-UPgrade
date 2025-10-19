from odoo import api, fields, models, _


class Location(models.Model):
    _name = 'custom.location'
    _description = "Location"

    name = fields.Char(string='Location Name', required=True)
    arabic_name = fields.Char(string='Arabic Name')
    latitude = fields.Float(string='Latitude')
    longitude = fields.Float(string='Longitude')

    short_name_ids = fields.Many2many(
        "custom.location.short.name",
        "location_short_name_rel",
        "location_id",
        "short_name_id",
        string="Short Names",
    )
