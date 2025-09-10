from odoo import models, fields, api


class Ugo2GiftDenomination(models.Model):
    _name = "ugo2gift.denomination"
    _description = "UGO2GIFT Denomination"

    brand_id = fields.Many2one(
        "ugo2gift.brand", string="Brand", help="The brand this denomination belongs to."
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        help="Currency code of the denomination (e.g., USD, EUR, INR).",
    )

    min_amount = fields.Float(
        string="Minimum Amount",
        help="The minimum allowed denomination amount for this brand.",
    )

    max_amount = fields.Float(
        string="Maximum Amount",
        help="The maximum allowed denomination amount for this brand.",
    )

    amount = fields.Float(
        string="Fixed Amount",
        help="The fixed denomination amount (if applicable). Leave empty if the brand supports variable amounts.",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        oldname="is_active",
        help="Indicates whether this denomination is active and available for use.",
    )

    @api.depends("brand_id", "currency_id", "amount")
    def _compute_display_name(self):
        for rec in self:
            brand = rec.brand_id.name or ""
            currency = rec.currency_id.name or ""
            if rec.amount:
                rec.display_name = f"{brand} - {rec.amount:.2f} {currency}"
            else:
                rec.display_name = f"{brand} ({currency})" if currency else brand
