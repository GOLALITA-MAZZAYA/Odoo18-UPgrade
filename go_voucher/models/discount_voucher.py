from odoo import models, fields, api, tools
from odoo.tools.translate import html_translate
import uuid
import base64

from odoo.addons.go_giftcard.models.ugo2gift_api_request import Ugo2GiftAPI


class DiscountVoucher(models.Model):
    _name = "discount.voucher"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Discount Voucher"

    _sql_constraints = [
        (
            "unique_voucher_code",
            "unique(code)",
            "Voucher Code must be unique.",
        )
    ]

    # =========================================================
    # Basic Info
    # =========================================================
    name = fields.Char(
        string="Voucher Name",
        help="Enter a name to identify the voucher (e.g., Summer Sale 2025).",
    )

    name_arabic = fields.Char(
        string="Voucher Name (Arabic)",
        help="Enter the voucher name in Arabic language only.",
    )

    code = fields.Char(
        string="Voucher Code",
        copy=False,
        help="Unique code that customers will use to redeem the voucher.",
    )
    logo = fields.Binary(
        string="Voucher Logo",
        help="Upload a logo or image to visually represent the voucher.",
    )
    merchant_ids = fields.Many2many(
        "res.partner",
        relation="merchant_voucher_rel",
        column2="merchant_id",
        column1="partner_id",
        domain=[("entity_type", "=", "merchant")],
        string="Merchants",
        help="Select the merchants where this voucher can be redeemed.",
    )
    organisation_ids = fields.Many2many(
        "res.partner",
        relation="organisation_voucher_rel",
        column2="organisation_id",
        column1="partner_id",
        domain=[("entity_type", "=", "organisation")],
        string="Organisations",
        help="Select the organisations associated with this voucher.",
    )
    voucher_category_id = fields.Many2one(
        "ugo2gift.category",
        string="Category",
        help="Select the category this voucher belongs to (e.g., Food, Travel, Shopping).",
    )
    country_id = fields.Many2one(
        "ugo2gift.country",
        string="Country",
        help="The country where this voucher can be used.",
    )

    # =========================================================
    # Discount & Value Settings
    # =========================================================
    discount_type = fields.Selection(
        [("percentage", "Percentage"), ("fixed_amount", "Fixed Amount")],
        default="percentage",
        string="Discount Type",
        tracking=True,
        help="Choose how the discount is applied:\n"
        "- Percentage: Customers receive a percentage discount.\n"
        "- Fixed Amount: Customers receive a fixed amount discount.",
    )
    discount_value = fields.Float(
        string="Discount Value",
        tracking=True,
        help="Enter the discount value. Interpretation depends on the selected Discount Type.",
    )
    voucher_amount = fields.Float(
        string="Voucher Amount",
        tracking=True,
        help="The base monetary value of the voucher.",
    )
    expiry_date = fields.Date(
        string="Expiry Date",
        tracking=True,
        help="The date after which this voucher will no longer be valid.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("expired", "Expired")],
        default="draft",
        string="Status",
        tracking=True,
        help="Current status of the voucher:\n"
        "- Draft: Not yet available.\n"
        "- Active: Available for use.\n"
        "- Expired: No longer valid.",
    )

    # =========================================================
    # Charges & Payments
    # =========================================================
    bank_charge = fields.Boolean(
        string="Bank Charge",
        help="Enable this if an additional bank charge applies when using the voucher.",
    )
    cash = fields.Boolean(
        string="Accept Cash",
        help="Enable this if the voucher can also be redeemed with a cash payment option.",
    )
    delivery_charge = fields.Float(
        string="Delivery Charge",
        help="Specify the delivery charge (if any) applied when using the voucher.",
    )

    # =========================================================
    # Merchant Info
    # =========================================================
    merchant_logo = fields.Binary(
        string="Merchant Logo",
        help="Upload the logo of the merchant associated with this voucher.",
    )
    phone = fields.Char(
        string="Phone Number",
        help="Merchant or support phone number for inquiries related to this voucher.",
    )

    # =========================================================
    # Usage Tracking
    # =========================================================
    redeemed_user_ids = fields.One2many(
        "voucher.redeemed.user",
        "discount_voucher_id",
        string="Redeemed Users",
        help="List of users who have redeemed this voucher.",
    )
    voucher_saved_ids = fields.One2many(
        "voucher.saved.user",
        "discount_voucher_id",
        string="Saved Users",
        help="List of users who have saved this voucher for later use.",
    )
    voucher_purchased_ids = fields.One2many(
        "voucher.purchased.user",
        "discount_voucher_id",
        string="Purchased Users",
        help="List of users who have purchased this voucher.",
    )

    # =========================================================
    # Terms & Instructions
    # =========================================================

    terms_condition = fields.Html(
        string="Terms & Conditions",
        help="Specify the terms and conditions applicable to this voucher.",
    )

    terms_condition_arabic = fields.Html(
        string="Terms & Conditions (Arabic)",
        help="Specify the voucher's terms and conditions in Arabic.",
    )

    instruction = fields.Html(
        string="Instructions",
        translate=html_translate,
        help="Provide any instructions or usage guidelines for the voucher.",
    )

    def action_activate(self):
        self.state ='active'

    def check_voucher_expiry(self):
        today = fields.Date.today()
        vouchers = self.search(
            [
                ("state", "!=", "expired"),
                ("expiry_date", "<", today)
            ]
        )
        if vouchers:
            vouchers.write({"state": "expired"})

    def get_skipcash_url(
        self,
        transaction_id,
        current_user,
        quantity,
        amount_after_discount
    ):
        api_url, merchant_key, merchant_password = (
            self.env["gift.card"]._check_skipcash_api_credentials()
        )

        uid = str(uuid.uuid4())

        voucher_amount = round(
            (quantity * amount_after_discount) * (1 + 0.0185) + 0.5, 2
        )

        payload = {
            "Uid": uid,
            "KeyId": merchant_key,
            "Amount": str(voucher_amount),
            "FirstName": current_user.partner_id.name,
            "LastName": current_user.partner_id.name,
            "Email": current_user.partner_id.email,
            "TransactionId": transaction_id,
        }

        signing_string = ",".join(f"{k}={v}" for k, v in payload.items())
        signature = self.env["gift.card"].hash_hmac(signing_string, merchant_password, raw_output=True)
        authorization = base64.b64encode(signature).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }

        skipcash_api = Ugo2GiftAPI(
            self.env, api_url, merchant_key, merchant_password, headers=headers
        )

        response = skipcash_api.create_skipcash_payment(payload)

        if response.get("success"):
            result_obj = response.get("data", {}).get("resultObj", {})
            return {
                "id": result_obj.get("id"),
                "pay_url": result_obj.get("payUrl"),
            }

        return {"error": response.get("message", "Failed to create Skipcash payment")}

    def action_convert_html_text(self, html):
        if not html:
            return ""
        return tools.html2plaintext(html)
