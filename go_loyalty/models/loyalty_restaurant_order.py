from odoo import fields, models,api,_


class LoyaltyRestaurantOrder(models.Model):
    _name = "loyalty.restaurant.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Restaurant Order"

    # =========================================================
    # Basic Information
    # =========================================================
    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        index=True,
        default="New",
        help="Unique reference number for the restaurant order.",
    )
    origin = fields.Char(
        string="Source Document",
        help="Reference to the source document (e.g. quotation, sales order) that generated this order.",
    )
    state = fields.Selection(
        [
            ("draft", "New"),
            ("sale", "Confirmed Order"),
            ("done", "Locked"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
        default="draft",
        help="Current status of the order.",
    )
    date_order = fields.Datetime(
        string="Order Date",
        required=True,
        index=True,
        copy=False,
        default=fields.Datetime.now,
        help="For draft orders: the creation date.\nFor confirmed orders: the confirmation date.",
    )
    note = fields.Text(
        string="Terms and conditions",
    )

    # =========================================================
    # Relations / Users
    # =========================================================

    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        index=True,
        tracking=2,
        default=lambda self: self.env.user,
        help="User responsible for handling this order.",
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        change_default=True,
        index=True,
        tracking=1,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Customer placing the restaurant order.",
    )
    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain="[('entity_type', '=', 'merchant')]",
        help="Merchant associated with this order (e.g., restaurant owner).",
    )

    # =========================================================
    # Customer Location
    # =========================================================
    partner_latitude = fields.Float(
        related="partner_id.partner_latitude",
        string="Customer Latitude",
        help="Latitude of the customer's delivery location.",
    )
    partner_longitude = fields.Float(
        related="partner_id.partner_longitude",
        string="Customer Longitude",
        help="Longitude of the customer's delivery location.",
    )

    # =========================================================
    # Pricing / Finance
    # =========================================================
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        check_company=True,
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        tracking=1,
        help="Pricelist used to calculate product prices for this order.",
    )
    currency_id = fields.Many2one(
        related="pricelist_id.currency_id",
        depends=["pricelist_id"],
        store=True,
        string="Currency",
        help="Currency used in this order, derived from the selected pricelist.",
    )
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_amount_all",
        tracking=5,
        help="Total order amount before taxes.",
    )
    amount_tax = fields.Monetary(
        string="Taxes",
        store=True,
        readonly=True,
        compute="_amount_all",
        help="Total taxes applied on the order.",
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        store=True,
        readonly=True,
        compute="_amount_all",
        tracking=4,
        help="Total order amount including taxes.",
    )

    # =========================================================
    # Company / Accounting
    # =========================================================
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company responsible for processing this order.",
    )
    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal Position",
        domain="[('company_id', '=', company_id)]",
        check_company=True,
        help="Fiscal position used to adapt taxes and accounts for the customer.",
    )

    # =========================================================
    # Voucher / Customer Details
    # =========================================================
    voucher_value = fields.Char(
        string="Voucher Value",
        oldname="x_voucher_value",
        help="Voucher value applied on this order, if any.",
    )
    voucher_applied = fields.Boolean(
        string="Voucher Applied",
        oldname="x_voucher_applied",
        help="Indicates whether a voucher has been applied to this order.",
    )
    customer_address_id = fields.Many2one(
        "user.address",
        string="Customer Address",
        oldname="x_customer_address_id",
        help="Delivery or pickup address provided by the customer.",
    )
    customer_phone = fields.Char(
        string="Customer Phone",
        oldname="x_customer_phone",
        help="Phone number of the customer placing the order.",
    )
    delivery_type = fields.Selection(
        [
            ("take_away", "Take Away"),
            ("delivery", "Delivery"),
        ],
        string="Delivery Type",
        oldname="x_delivery_type",
        help="Specifies whether the order is for delivery or take-away.",
    )

    # =========================================================
    # Order Lines
    # =========================================================
    line_ids = fields.One2many(
        "loyalty.restaurant.order.line",
        "order_id",
        string="Order Lines",
        help="List of individual products or services included in this order.",
    )

    @api.depends(
        "line_ids",
        "line_ids.price_subtotal",
        "line_ids.price_tax"
    )
    def _amount_all(self):
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.line_ids)
            amount_tax = sum(line.price_tax for line in order.line_ids)
            order.amount_untaxed = amount_untaxed
            order.amount_tax = amount_tax
            order.amount_total = amount_untaxed + amount_tax

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "company_id" in vals:
                self = self.with_company(vals["company_id"])

            if vals.get("name", _("New")) == _("New"):
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(
                        self, fields.Datetime.to_datetime(vals["date_order"])
                    )
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "loyalty.restaurant.order", sequence_date=seq_date
                ) or _("New")

            if "pricelist_id" not in vals and vals.get("partner_id"):
                partner = self.env["res.partner"].browse(vals["partner_id"])
                vals["pricelist_id"] = partner.property_product_pricelist.id

        orders = super(LoyaltyRestaurantOrder, self).create(vals_list)
        return orders

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        self = self.with_company(self.company_id)
        self.pricelist_id = (
            self.partner_id.property_product_pricelist.id if self.partner_id else False
        )

    def action_confirm(self):
        self.state = "sale"

    def action_cancel(self):
        self.state = "cancel"

    def action_draft(self):
        self.state = "draft"
