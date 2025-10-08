from odoo import models, fields, api


class MerchantBranch(models.Model):
    _name = "merchant.branch"
    _description = "Merchant Branch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, name, id"


    # Core
    name = fields.Char(required=True, tracking=True, help="Public branch name.")
    name_ar = fields.Char(string="Name (Arabic)", help="Arabic name for the branch.")
    code = fields.Char(
        string="Code",
        size=32,
        index=True,
        tracking=True,
        help="Optional short code to identify this branch (unique per Partner).",
    )
    active = fields.Boolean(default=True, index=True)

    # Relations
    partner_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        required=True,
        index=True,
        ondelete="cascade",
        tracking=True,
        help="Owning merchant/company for this branch.",
    )
    partner_sub_id = fields.Many2one(
        "res.partner",
        string="Partner Sub Account",
        ondelete="set null",
        help="Optional sub-account/contact under the same commercial entity.",
    )

    # Constraints
    _sql_constraints = [
        (
            "uniq_branch_code_per_partner",
            "unique(partner_id, code)",
            "Branch code must be unique per Merchant.",
        )
    ]

    @api.depends("name", "code", "partner_id")
    def _compute_display_name(self):
        for rec in self:
            left = f"[{rec.code}] " if rec.code else ""
            right = rec.name or ""
            rec.display_name = f"{left}{right}"


