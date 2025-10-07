from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LoyaltySale(models.Model):
    _name = "loyalty.sale"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Loyalty Sale Transaction"

    name = fields.Char(string="Reference")
    date = fields.Datetime(
        string="Transaction Date",
        default=fields.Datetime.now(),
        help="Date and time when the transaction took place.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="Status",
        tracking=True,
        help="Indicates the current stage of the transaction.",
    )
    user_id = fields.Many2one(
        "res.users", string="Responsible User", default=lambda self: self.env.user.id
    )
    note = fields.Text(string="Notes")

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        help="Customer involved in this loyalty transaction.",
    )
    organisation_id = fields.Many2one(
        related="partner_id.parent_id", string="Organisation", store=True
    )
    employee_type = fields.Selection(
        related="partner_id.employee_type", string="Employee Type", tracking=True
    )
    phone = fields.Char(related="partner_id.phone", string="Customer Phone")
    profile = fields.Image(
        related="partner_id.image_512", string="Customer Profile Image"
    )

    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        default=lambda self: self.env.user.partner_id.id,
        help="Merchant or business partner processing this transaction.",
    )
    # merchant_category_id = fields.Many2one(
    #     'partner.category',
    #     related='merchant_id.partner_category_id',
    #     store=True,
    #     string='Merchant Category'
    # )

    logo = fields.Image(related="organisation_id.image_512", string="Organisation Logo")

    # --------------------------------------------------------
    # Transaction Details
    # --------------------------------------------------------
    amount = fields.Float(
        string="Transaction Amount",
        required=True,
        compute="_compute_total_amount",
    )
    transfer_point_type = fields.Selection(
        [
            ("redeem", "Redeem"),
            ("reward", "Reward"),
        ],
        default="reward",
        tracking=True,
        string="Transaction Type",
        help="Defines whether this transaction rewards or redeems points.",
    )
    points = fields.Integer(string="Points Earned")
    discount = fields.Float(string="Discount")
    extra_merchant_discount = fields.Float(string="Extra Merchant Discount")
    final_amount = fields.Float(
        string="Amount to Pay",
        compute="_compute_amount",
        store=True,
        help="Final payable amount after applying discounts and redemptions.",
    )

    current_points = fields.Integer(
        related="partner_id.points", string="Customer Available Points"
    )
    merchant_points = fields.Integer(
        related="merchant_id.points", string="Merchant Available Points"
    )
    rule_id = fields.Many2one(
        "loyalty.rule",
        string="Loyalty Rule",
        help="Rule used to calculate points or rewards for this transaction.",
    )
    transaction_ids = fields.One2many(
        "loyalty.point.transfer.line", "sale_id", string="Loyalty Point Transfers"
    )

    # --------------------------------------------------------
    # Products
    # --------------------------------------------------------
    include_product = fields.Boolean(
        string="Include Products"
    )
    sale_line_ids = fields.One2many(
        "loyalty.sale.line", "sale_id", string="Transaction Products"
    )

    @api.depends("amount", "discount", "extra_merchant_discount")
    def _compute_amount(self):
        for sale in self:
            sale.final_amount = (
                sale.amount - sale.discount - sale.extra_merchant_discount
            )

    @api.depends("sale_line_ids", "sale_line_ids.subtotal")
    def _compute_total_amount(self):
        for sale in self:
            sale.amount = sum(sale.sale_line_ids.mapped("subtotal"))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        if self.partner_id:
            self.rule_id = self.partner_id._get_rule()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = vals.get("name") or self.env["ir.sequence"].next_by_code(
                "loyalty.sale"
            )

        sales = super().create(vals_list)

        # # Apply onchange logic if rule_id not provided
        # for sale in sales.filtered(lambda s: not s.rule_id):
        #     sale.onchange_partner_id()
        #     sale.onchange_amount_transfer_point_type()

        return sales

    def action_cancel(self):
        self.state = "cancel"

    def perform_validation(self):
        if self.transfer_point_type == "redeem" and self.current_points < 1:
            raise UserError(_("You don't have enough point to redeem."))
        if self.amount < 1:
            raise UserError(_("Amount should be positive"))

    def action_confirm(self):
        self.perform_validation()

        points_list = []
        now = fields.Datetime.now()

        if self.transfer_point_type == "reward":
            points = 0.1 * self.amount

            if self.merchant_id and self.merchant_id.points < points:
                raise UserError(_("Merchant does not have enough points to transfer"))

            self.points = points

            points_list = [
                {
                    "sale_id": self.id,
                    "debit": points,
                    "date": now,
                    "state": "post",
                    "partner_id": self.merchant_id.id,
                    "name": self.name,
                },
                {
                    "sale_id": self.id,
                    "credit": points,
                    "date": now,
                    "state": "post",
                    "partner_id": self.partner_id.id,
                    "name": self.name,
                },
            ]

        elif self.transfer_point_type == "redeem":
            discount = 0.05 * self.current_points
            self.discount = discount

            points_list = [
                {
                    "sale_id": self.id,
                    "debit": self.current_points,
                    "date": now,
                    "state": "post",
                    "partner_id": self.partner_id.id,
                    "name": self.name,
                },
                {
                    "sale_id": self.id,
                    "credit": self.current_points,
                    "date": now,
                    "state": "post",
                    "partner_id": self.merchant_id.id,
                    "name": self.name,
                },
            ]

        if points_list:
            self.env["loyalty.point.transfer.line"].create(points_list)

        self.state = "confirm"
        return True
