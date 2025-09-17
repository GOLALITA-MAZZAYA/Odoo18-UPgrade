from odoo import models, fields, api
from odoo.exceptions import ValidationError


class VoucherPurchasedUser(models.Model):
    _name = "voucher.purchased.user"
    _description = "Purchased Voucher"

    user_id = fields.Many2one(
        "res.users", string="User", help="The user who purchased the voucher."
    )
    purchase_date = fields.Datetime(
        string="Purchase Date", help="The date and time when the voucher was purchased."
    )
    discount_voucher_id = fields.Many2one(
        "discount.voucher",
        string="Discount Voucher",
        ondelete="cascade",
        help="The voucher that was purchased.",
    )
    quantity = fields.Integer(
        string="Quantity", default=1, help="Number of voucher units purchased."
    )
    voucher_price = fields.Float(string="Unit Price", help="Price per single voucher.")
    total_price = fields.Float(
        string="Total Price",
        compute="_compute_total_price",
        store=True,
        help="Automatically calculated as Quantity × Unit Price.",
    )
    payment_url = fields.Char(
        string="Payment URL",
        help="URL link where the user can complete the payment for this voucher.",
    )

    payment_status = fields.Char(
        string="Payment Status",
        default="Not Paid",
        help="Current status of the payment for this purchase.",
    )

    payment_id = fields.Char(
        string="Payment ID",
        help="Reference ID from the payment gateway for tracking the payment.",
    )
    vis_id = fields.Char(
        string="Visa ID",
        help="Visa transaction reference ID, if payment was made through Visa.",
    )
    remark = fields.Char(
        string="Remark", help="Additional notes or comments related to this purchase."
    )

    @api.depends("quantity", "voucher_price")
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.quantity * rec.voucher_price

    @api.constrains("quantity")
    def _check_quantity(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Quantity must be greater than 0.")

    @api.depends("user_id.name", "discount_voucher_id.name", "quantity")
    def _compute_display_name(self):
        for rec in self:
            user = rec.user_id.name or "Unknown User"
            voucher = rec.discount_voucher_id.name or "No Voucher"
            qty = rec.quantity or 1
            rec.display_name = f"{user} purchased {qty} × {voucher}"
