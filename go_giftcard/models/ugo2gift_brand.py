import base64
import hashlib
import hmac
from datetime import datetime

from odoo.exceptions import ValidationError

from odoo import models, fields
from .ugo2gift_api_request import Ugo2GiftAPI


class Ugo2GiftBrand(models.Model):
    _name = "ugo2gift.brand"
    _description = "UGO2GIFT Brand"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # --------------------------
    # Identification
    # --------------------------

    brand_code = fields.Char(
        string="Brand Code",
        index=True,
        help="Unique code provided by UGO2GIFT to identify the brand.",
    )

    brand_id = fields.Integer(
        string="Brand ID",
        index=True,
    )

    name = fields.Char(
        string="Brand Name", required=True, help="The official name of the brand."
    )
    tagline = fields.Char(
        string="Tagline", help="Short tagline or slogan associated with the brand."
    )

    # --------------------------
    # Status & Flags
    # --------------------------

    active = fields.Boolean(
        string="Active",
        default=True,
        oldname="is_active",
        help="Indicates whether this brand is currently active and available.",
    )
    is_generic = fields.Boolean(
        string="Generic Brand",
        default=False,
        help="Check if this is a generic brand used as a placeholder.",
    )
    pin_redeemable = fields.Boolean(
        string="PIN Redeemable",
        default=False,
        help="If enabled, the gift card can be redeemed using a PIN code.",
    )
    variable_amount = fields.Boolean(
        string="Variable Amount",
        default=False,
        help="If enabled, customers can purchase gift cards with variable amounts.",
    )
    validity_in_months = fields.Integer(
        string="Validity (Months)",
        default=6,
        help="Validity period of the gift card in months.",
    )

    # --------------------------
    # Media
    # --------------------------

    logo_url = fields.Char(
        string="Logo URL",
        help="Direct URL to the brand's logo image.",
        oldname="logo",
    )

    product_image_url = fields.Char(
        string="Product Image URL",
        help="Direct URL to the brand's main product image.",
        oldname="product_image",
    )

    image_gallery_ids = fields.One2many(
        "ugo2gift.image",
        "brand_id",
        string="Image Gallery",
        help="Additional images related to this brand.",
        oldname="image_gallery",
    )

    # --------------------------
    # Relations
    # --------------------------

    country_ids = fields.Many2many(
        "ugo2gift.country",
        string="Available in Countries",
        help="Countries where this brand is available or valid."
    )

    category_ids = fields.Many2many(
        "ugo2gift.category",
        string="Categories",
        help="Categories associated with this brand.",
    )
    denomination_ids = fields.One2many(
        "ugo2gift.denomination",
        "brand_id",
        string="Denominations",
        help="Available denominations for this brand.",
    )

    # --------------------------
    # Redemption
    # --------------------------

    brand_accepted_currency_id = fields.Many2one(
        "res.currency",
        string="Accepted Currency",
        help="Currency accepted by this brand for redemption.",
    )
    redemption_type = fields.Char(
        string="Redemption Type",
        help="Specifies how the gift card can be redeemed (online, in-store, etc.).",
    )
    redemption_instructions = fields.Text(
        string="Redemption Instructions",
        translate=True,
        help="Instructions on how to redeem the gift card.",
    )
    detail_url = fields.Char(
        string="Details Page URL",
        help="URL of the brand details page provided by UGO2GIFT.",
    )
    locations_url = fields.Char(
        string="Locations Page URL",
        help="URL to check store locations where the gift card can be redeemed.",
    )

    description = fields.Text(
        string="Description",
        translate=True,
        help="Detailed description of the brand and its gift card.",
    )
    rate = fields.Float(string="Currency Conversion Rate", oldname="x_rate")

    def action_fetch_brand(self):
        api_url, api_key, api_secret = self._check_api_credentials()
        headers = self._generate_headers(api_key)

        gift_api = Ugo2GiftAPI(self.env, api_url, api_key, api_secret, headers)
        response = gift_api.get_brand(endpoint="brands")

        brands = response.get("data") or []

        if not response.get("success") or not brands:
            msg = response.get("error") or "No brand data received from API."
            gift_api.post_message(msg)
            return False

        for brand_data in brands:
            brand_id = brand_data.get("id")
            if not brand_id:
                gift_api.post_message("Warning: Skipping brand with missing ID.")
                continue

            vals = self._prepare_brand_data(brand_data)
            brand_record = self.search([("brand_id", "=", brand_id)], limit=1)

            if brand_record:
                brand_record.write(vals)
            else:
                self.create(vals)

        return {
            "effect": {
                "fadeout": "slow",
                "message": "Successfully synced brands",
                "type": "rainbow_man",
            }
        }

    def _generate_headers(self, api_key):
        date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        message = f"date: {date}"

        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
            ).digest()
        ).decode("utf-8")

        return {
            "date": date,
            "X-Api-Key": api_key,
            "Accept": "application/json",
            "Authorization": f'Signature keyId="{api_key}",algorithm="hmac-sha256",headers="date",signature="{signature}"',
        }

    def _prepare_brand_data(self, brand):
        return {
            "brand_id": brand.get("id") or 0,
            "brand_code": brand.get("brand_code") or "",
            "name": brand.get("name") or "Unnamed Brand",
            "logo": brand.get("logo") or "",
            "is_active": brand.get("is_active", True),
            "is_generic": brand.get("is_generic", False),
            "pin_redeemable": brand.get("pin_redeemable", False),
            "validity_in_months": brand.get("validity_in_months") or 6,
            "variable_amount": brand.get("variable_amount", False),
            "tagline": brand.get("tagline") or "",
            "description": brand.get("description") or "",
            "brand_accepted_currency": brand.get("brand_accepted_currency") or "",
            "redemption_type": brand.get("redemption_type") or "",
            "redemption_instructions": brand.get("redemption_instructions") or "",
            "detail_url": brand.get("detail_url") or "",
            "locations_url": brand.get("locations_url") or "",
            "product_image": brand.get("product_image") or "",
            "country_ids": self.get_country_data(brand) or [],
            "denomination_ids": self.get_denomination_data(brand) or [],
            "category_ids": self.get_category_data(brand) or [],
            "image_gallery": self.get_image_gallery_data(brand) or [],
        }

    def get_country_data(self, brand):
        country_info = brand.get("country", {})
        country_code = country_info.get("code")
        if country_code:
            return self.env["ugo2gift.country"].search([("code", "=", country_code)])
        return self.env["ugo2gift.country"]

    def get_category_data(self, brand):
        category_ids = []
        for category_data in brand.get("categories", []):
            category_id = category_data.get("id")
            if category_id:
                category = self.env["ugo2gift.category"].search(
                    [("category_id", "=", category_id)], limit=1
                )
                if category:
                    category_ids.append(category.id)

        return category_ids

    def get_image_gallery_data(self, brand):
        image_gallery_records = []
        for image in brand.get("image_gallery", []):
            image_gallery_records.append((0, 0, {"image": image.get("image")}))
        return image_gallery_records

    def get_denomination_data(self, brand):
        denominations = []
        for currency, amounts in brand.get("denominations", {}).items():
            if isinstance(amounts, dict):
                amounts = [amounts]
            elif not isinstance(amounts, list):
                continue  # Skip invalid structures

            for amount_data in amounts:
                res = {
                    "currency": currency,
                    "amount": amount_data.get("amount", 0),
                    "is_active": amount_data.get("is_active", False),
                    "min_amount": amount_data.get("min", 0),
                    "max_amount": amount_data.get("max", 0),
                }
                denominations.append((0, 0, res))
        return denominations
