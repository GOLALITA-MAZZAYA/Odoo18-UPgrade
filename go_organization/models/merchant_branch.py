from odoo import models, fields, api


class MerchantBranch(models.Model):
    _name = "merchant.branch"
    _description = "Merchant Branch"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "partner_id, name, id"
    _rec_name = "display_name"

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

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="partner_id.company_id",
        store=True,
        index=True,
        readonly=True,
    )

    # Smart display
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
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

    def name_search(self, name="", args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("code", "ilike", name), ("name", "ilike", name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def name_get(self):
        result = []
        for rec in self:
            disp = rec.display_name or rec.name or ""
            # Add merchant suffix to disambiguate in dropdowns
            if rec.partner_id:
                disp = f"{disp} — {rec.partner_id.display_name}"
            result.append((rec.id, disp))
        return result
