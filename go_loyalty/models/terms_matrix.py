from odoo import models, fields, api


class TermsMatrix(models.Model):
    _name = "terms.matrix"
    _description = "Terms Matrix"
    _order = "create_date desc"

    res_partner_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        required=True,
        domain=[("entity_type", "=", "merchant")],
        index=True,
        help="Main merchant associated with these terms.",
    )

    organisation_id = fields.Many2many(
        "res.partner",
        "terms_matrix_res_partner_rel",
        "terms_matrix_id",
        "partner_id",
        string="Organisations",
        domain=[("entity_type", "=", "organisation")],
        help="Organisations covered by these terms.",
    )

    terms_condition = fields.Html(
        string="Terms and Conditions", help="Terms and conditions in default language."
    )

    terms_condition_ar = fields.Html(
        string="Terms and Conditions (Arabic)",
        help="Terms and conditions in Arabic language.",
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
