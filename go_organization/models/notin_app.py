from odoo import models, fields


class NotinApp(models.Model):

    _name = "notin.app"
    _description = "Not Linked App"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name, code, id"

    name = fields.Char(required=True, tracking=True, help="App name as shown to users.")
    code = fields.Char(
        required=True,
        index=True,
        size=64,
        tracking=True,
        help="Unique short code for the app.",
    )
    active = fields.Boolean(default=True, index=True)

    parent_id = fields.Many2one(
        "res.partner",
        string="Linked Organisation",
        ondelete="set null",
        index=True,
        help="Organisation this app visibility rule is linked with (optional).",
    )
