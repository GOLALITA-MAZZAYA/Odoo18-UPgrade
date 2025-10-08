from odoo import models, fields


class NotinApp(models.Model):
    _name = "notin.app"
    _description = "Not Linked APP"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        required=True,
        index=True,
        help="Name of the application.",
    )
    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Unique code for the application.",
    )
    parent_id = fields.Many2one(
        "res.partner",
        string="Linked Organisation",
        domain=[("entity_type", "=", "organisation")],
        help="Organisation associated with this app, if any.",
    )
