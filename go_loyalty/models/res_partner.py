from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    points = fields.Integer(
        string="Loyalty Points", compute="_compute_points", store=True
    )

    line_ids = fields.One2many("loyalty.point.transfer.line", "partner_id")

    @api.depends("line_ids.partner_id", "line_ids.balance")
    def _compute_points(self):
        for p in self:
            p.points = sum(l.balance for l in p.line_ids)
