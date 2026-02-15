from odoo import fields, models, api
from odoo.tools.misc import get_lang


class LoyaltyRestaurantOrderLine(models.Model):
    _name = "loyalty.restaurant.order.line"
    _description = "Restaurant Order Line"

    # =========================================================
    # Order Reference
    # =========================================================
    order_id = fields.Many2one(
        "loyalty.restaurant.order",
        string="Order Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
        help="The restaurant order this line belongs to.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Defines the display order of the order lines.",
    )
    state = fields.Selection(
        related="order_id.state",
        string="Order Status",
        readonly=True,
        copy=False,
        default="draft",
        help="Status of the parent order (Draft, Confirmed, Completed, or Cancelled).",
    )

    # =========================================================
    # Product Information
    # =========================================================
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True,
        ondelete="restrict",
        check_company=True,
        help="The product selected for this order line.",
    )
    product_template_id = fields.Many2one(
        "product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
        help="Technical field that links to the product template of the selected product.",
    )
    name = fields.Text(
        string="Description",
        required=True,
        help="Description of the product or service being ordered.",
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        required=True,
        default=1.0,
        help="The number of units of the product ordered.",
    )
    product_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        help="Unit of measure for the specified product.",
    )
    product_uom_category_id = fields.Many2one(
        related="product_id.uom_id.category_id",
        readonly=True,
        string="Unit of Measure Category",
        help="Technical field for ensuring the selected unit of measure belongs to the correct category.",
    )

    # =========================================================
    # Pricing / Finance
    # =========================================================
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
        digits="Product Price",
        default=0.0,
        help="Unit selling price of the product.",
    )
    discount = fields.Float(
        string="Discount (%)",
        digits="Discount",
        default=0.0,
        help="Discount percentage applied to this order line.",
    )
    tax_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        context={"active_test": False},
        help="Taxes applied to the product for this order line.",
    )
    price_subtotal = fields.Monetary(
        compute="_compute_amount",
        string="Subtotal",
        store=True,
        currency_field="currency_id",
        help="Line amount before taxes.",
    )
    price_tax = fields.Float(
        compute="_compute_amount",
        string="Total Tax",
        store=True,
        currency_field="currency_id",
        help="Tax amount for this order line.",
    )
    price_total = fields.Monetary(
        compute="_compute_amount",
        string="Total Amount",
        store=True,
        currency_field="currency_id",
        help="Line total including taxes.",
    )

    # =========================================================
    # Relations / Context
    # =========================================================
    salesman_id = fields.Many2one(
        related="order_id.user_id",
        store=True,
        string="Salesperson",
        readonly=True,
        help="Salesperson responsible for the order.",
    )
    currency_id = fields.Many2one(
        related="order_id.currency_id",
        depends=["order_id.currency_id"],
        store=True,
        string="Currency",
        help="Currency used for this order line.",
    )
    company_id = fields.Many2one(
        related="order_id.company_id",
        string="Company",
        store=True,
        index=True,
        help="Company related to the order line.",
    )
    partner_id = fields.Many2one(
        related="order_id.partner_id",
        store=True,
        string="Customer",
        help="Customer linked to the parent order.",
    )

    @api.depends("product_uom_qty", "discount", "price_unit", "tax_id")
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                currency=line.order_id.currency_id,
                quantity=line.product_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.price_subtotal = taxes.get("total_excluded", 0.0)
            line.price_total = taxes.get("total_included", 0.0)
            line.price_tax = sum(t.get("amount", 0.0) for t in taxes.get("taxes", []))

    @api.onchange("product_id")
    def product_id_change(self):
        if not self.product_id:
            return

        if not self.product_uom or self.product_id.uom_id != self.product_uom:
            self.product_uom = self.product_id.uom_id
            self.product_uom_qty = self.product_uom_qty or 1.0

        lang = get_lang(self.env, self.order_id.partner_id.lang).code
        product = self.product_id.with_context(
            lang=lang,
            partner=self.order_id.partner_id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = product.lst_price

        self.name = product.display_name

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = (
                line.order_id.fiscal_position_id
                or line.order_id.fiscal_position_id._get_fiscal_position(
                    line.partner_id
                )
            )

            taxes = line.product_id.taxes_id.filtered(
                lambda t: t.company_id == line.env.company
            )
            line.tax_id = fpos.map_tax(taxes)
