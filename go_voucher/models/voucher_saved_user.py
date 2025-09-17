from odoo import models, fields,api


class VoucherSavedUser(models.Model):
    _name = "voucher.saved.user"
    _description = "Saved Voucher"

    user_id = fields.Many2one(
        "res.users", string="User", help="The user who saved the voucher."
    )

    saved_date = fields.Datetime(
        string="Saved Date", help="The date and time when the voucher was saved."
    )

    discount_voucher_id = fields.Many2one(
        "discount.voucher",
        string="Discount Voucher",
        ondelete="cascade",
        help="The voucher that was saved by the user.",
    )

    @api.depends("user_id.name", "discount_voucher_id.name")
    def _compute_display_name(self):
        for rec in self:
            user = rec.user_id.name or "Unknown User"
            voucher = rec.discount_voucher_id.name or "No Voucher"
            rec.display_name = f"{user} - {voucher}"
