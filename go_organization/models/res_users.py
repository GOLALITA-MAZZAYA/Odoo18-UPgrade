from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    token = fields.Char()
