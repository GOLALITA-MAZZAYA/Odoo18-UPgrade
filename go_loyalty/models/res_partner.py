from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    points = fields.Integer(
        string="Loyalty Points", compute="_compute_points", store=True
    )

    line_ids = fields.One2many("loyalty.point.transfer.line", "partner_id")

    employee_type = fields.Selection(
        [("vip", "VIP"), ("standard", "Standard")],
        string="Employee Type",
        help="Category for organisation employees.",
    )

    @api.depends("line_ids.partner_id", "line_ids.balance")
    def _compute_points(self):
        for p in self:
            p.points = sum(l.balance for l in p.line_ids)

    def _get_rule(self):
        Rule = self.env["loyalty.rule"]
        entity_map = {
            "organisation": "organisation",
            "merchant": "merchant",
            "employee_standard": "employee_standard",
            "employee_vip": "employee_vip",
        }

        if self.entity_type in ["organisation", "merchant"]:
            entity = entity_map[self.entity_type]
            partner = self
        elif self.entity_type == "employee":
            entity = entity_map[f"employee_{self.employee_type}"]
            partner = self.parent_id
        else:
            return Rule

        return Rule.search(
            [("entity", "=", entity), ("partner_id", "=", partner.id)], limit=1
        )
