from odoo import models, fields, api


class ContractMatrix(models.Model):
    _name = "contract.matrix"
    _description = "Contract Matrix"
    _order = "create_date desc"

    res_partner_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        required=True,
        domain=[("entity_type", "=", "merchant")],
        index=True,
        help="Main merchant associated with this contract.",
    )

    organisation_id = fields.Many2many(
        "res.partner",
        "contract_matrix_res_partner_rel",
        "contract_matrix_id",
        "partner_id",
        string="Organisations",
        domain=[("entity_type", "=", "organisation")],
    )

    contract_file = fields.Binary(
        string="Contract File",
        attachment=True,
        store=True,
        help="Upload or attach the signed contract document here.",
    )
    contract_filename = fields.Char(string="Contract File Name")

    contract_file_url = fields.Char(
        string="Contract File URL",
        compute="_compute_contract_file_url",
        store=True,
        help="Direct download link for the attached contract file.",
    )

    @api.depends("contract_file", "contract_filename")
    def _compute_contract_file_url(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for record in self:
            record.contract_file_url = (
                f"{base_url}/web/content/contract.matrix/{record.id}/contract_file/{record.contract_filename}?download=true"
                if record.contract_file
                else ""
            )

    @api.depends("res_partner_id", "create_date")
    def _compute_display_name(self):
        for record in self:
            merchant = record.res_partner_id.name or "Unknown Merchant"
            date_str = (
                fields.Date.to_string(record.create_date.date())
                if record.create_date
                else ""
            )

            record.display_name = f"{merchant} ({date_str})"
