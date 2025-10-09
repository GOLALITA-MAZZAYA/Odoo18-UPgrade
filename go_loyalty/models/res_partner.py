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

    is_token_permanent = fields.Boolean(
        string="Permanent API Token",
        help="If enabled, the user's API token will remain permanent and will not be regenerated automatically.",
    )

    from_website = fields.Boolean()

    entity_type = fields.Selection(
        [
            ("platform", "Platform"),
            ("organisation", "Organisation"),
            ("merchant", "Merchant"),
            ("employee", "Employee"),
            ("family", "Family Member"),
        ],
        string="Entity Type",
        oldname="go_entity",
        index=True,
        required=True,
        help="Functional role of the contact in your program.",
    )

    phone_verified = fields.Boolean()

    moi_last_name = fields.Char(oldname="x_moi_last_name")
    family_head_member_id = fields.Many2one("res.partner")

    org_type = fields.Selection(
        selection=[
            ("sjc", "SJC"),
            ("gulfexchange", "Gulf Exchange"),
            ("golalita", "Golalita"),
            ("daam", "DAAM"),
            ("qatarinsurance", "Qatar Insurance"),
            ("masrif", "Masrif"),
            ("barwa", "Barwa"),
            ("alzamanexchange", "Alzaman Exchange"),
            ("moi", "MOI"),
            ("qatar_post", "Qatar Post"),
            ("beema", "Beema"),
            ("hayyakam", "Hayyakam"),
            ("qlm", "QLM"),
        ],
        string="Associated Organisation",
        copy=True,
        store=True,
        oldname="x_org_type"
    )

    user_expiry = fields.Date(oldname="x_user_expiry")

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
