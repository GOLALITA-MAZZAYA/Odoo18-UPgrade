from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_in_offer = fields.Boolean(
        string="Included in Offer",
        help="Indicates if the product is part of an active offer.",
    )
    offer_label = fields.Char(string="Offer Label", help="Label to describe the offer.")
    offer_type = fields.Selection(
        [
            ("b1g1", "Buy 1 Get 1"),
            ("discount", "Discount"),
            ("promocode", "Promocode"),
            ("giftcard", "Gift Card"),
        ],
        string="Offer Type",
        help="Type of promotional offer applied.",
    )

    discount_flat = fields.Float(string="Flat Discount", oldname="discount")

    discount_percent = fields.Float(
        string="Discount (%)",
        help="Percentage discount if offer type is 'Discount'.",
        oldname="x_offer_type_discount",
    )

    promo_code = fields.Char(
        string="Promo Code",
        help="Promo code to use if offer type is 'Promocode'.",
        oldname="x_offer_type_promo_code",
    )

    start_date = fields.Datetime(
        string="Offer Start Date", help="Start date of the offer."
    )

    end_date = fields.Datetime(string="Offer End Date", help="End date of the offer.")

    usage_limit = fields.Integer(
        string="Usage Limit",
        help="Maximum number of times the offer can be used.",
        oldname="x_limit_use",
    )

    offer_attachment = fields.Binary(
        string="Offer Attachment",
        help="Upload a document/image with offer details.",
        oldname="x_offer_copy",
    )

    offer_attachment_filename = fields.Char(string="Offer File Name")

    offer_on_homepage = fields.Boolean(
        string="Show on Home Page",
        help="Display this product as a featured offer.",
        oldname="x_home_offer",
    )

    min_purchase_qty = fields.Float(
        string="Minimum Purchase Quantity",
        help="Minimum quantity required for the offer.",
        oldname="min_quantity",
    )

    max_purchase_qty = fields.Float(
        string="Maximum Purchase Quantity",
        help="Maximum quantity allowed for the offer.",
        oldname="max_quantity",
    )

    offer_limit_ids = fields.One2many(
        "offer.limits",
        "product_id",
        string="Offer Limits",
        help="Limits related to this offer.",
    )

    multi_offer_ids = fields.One2many(
        "multi.offers",
        "product_id",
        string="Multiple Offers",
        help="Multiple offer records linked to this product.",
    )

    expired_offer = fields.Boolean(
        string="Expired Offer", help="Indicates if this product's offer has expired."
    )

    is_restaurant_item = fields.Boolean(
        string="Restaurant Item",
        help="Indicates if the product is part of a restaurant menu.",
    )

    # ──────────────────────────────
    # EMPLOYEE & ACCESS CONTROL
    # ──────────────────────────────

    employee_type = fields.Selection(
        selection=[
            ("vip", "VIP"),
            ("standard", "Standard"),
            ("both", "Both"),
        ],
        string="Employee Type",
        help="Select whether the employee is VIP, Standard, or Both.",
        oldname="x_for_employee_type",
    )

    # ──────────────────────────────
    # UI / UX & LABELS
    # ──────────────────────────────

    sequence = fields.Integer(
        string="Sequence",
        help="Used to control product display order in lists.",
        oldname="x_sequence",
    )

    product_sticker_ids = fields.Many2many(
        "product.sticker",
        string="Product Stickers",
        help="Visual stickers like 'New', 'Trending', etc.",
    )

    # ──────────────────────────────
    # MISCELLANEOUS
    # ──────────────────────────────

    points = fields.Float(
        string="Reward Points",
        help="Points earned for purchasing this product.",
        oldname="x_point",
    )

    favourite_customer_ids = fields.One2many(
        "favourite.product",
        "product_id",
        string="Favourite Customers",
        help="Customers who favorited this product.",
        oldname="favourite_partner_ids",
    )

    branch_ids = fields.Many2many(
        "res.partner",
        "branch_partner_users_rel",
        "product_id",
        "branch_id",
        string="Available Branches",
        help="Branches where this product is available.",
    )

    not_linked_app_ids = fields.Many2many(
        "notin.app",
        "product_not_linked_rel",
        "product_id",
        "not_linked_id",
        string="Excluded from Apps",
        help="Apps where this product should not appear.",
    )

    # ──────────────────────────────
    # TECHNICAL / STATE
    # ──────────────────────────────

    state = fields.Selection(
        [("draft", "Draft"), ("pending", "Approval Pending"), ("publish", "Published")],
        default="draft",
        string="Status",
        tracking=True,
        help="Product publishing status.",
    )

    ar_description = fields.Text(
        string="Additional Description",
        translate=True,
        help="Extra description for internal or external use. This field is translatable.",
    )

    product_tags_ids = fields.Many2many("product.tags", string="Product Tags")

    @api.model
    def default_get(self, fields_list):
        res = super(ProductTemplate, self).default_get(fields_list)
        if self.env.context.get("from_product_offer_menu"):
            res.update({"is_in_offer": True, "sale_ok": False})
        return res

