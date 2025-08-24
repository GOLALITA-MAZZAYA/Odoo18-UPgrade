from odoo import models, fields

class PartnerCategory(models.Model):
    _name = "partner.category"
    _description = "Partner Category"
    _order = "name, id"

    name = fields.Char(required=True, translate=False)
    color = fields.Integer(string="Color Index", help="Optional color for tags.")

    _sql_constraints = [
        ("uniq_partner_category_name", "unique(name)", "Category name must be unique."),
    ]
