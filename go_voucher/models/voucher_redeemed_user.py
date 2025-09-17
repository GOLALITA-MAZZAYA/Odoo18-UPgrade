from odoo import models, fields, api


class VoucherRedeemedUser(models.Model):
    _name = "voucher.redeemed.user"
    _description = "Redeemed Voucher"

    user_id = fields.Many2one(
        "res.users", string="User", help="The user who redeemed this voucher."
    )

    redeemed_date = fields.Datetime(
        string="Redeemed Date", help="The date and time when the voucher was redeemed."
    )

    discount_voucher_id = fields.Many2one(
        "discount.voucher",
        string="Discount Voucher",
        ondelete="cascade",
        help="The voucher that was redeemed by the user.",
    )

    @api.depends("user_id.name", "discount_voucher_id.name")
    def _compute_display_name(self):
        for rec in self:
            user = rec.user_id.name or "Unknown User"
            voucher = rec.discount_voucher_id.name or "No Voucher"
            rec.display_name = f"{user} - {voucher}"
