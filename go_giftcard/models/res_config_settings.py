from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # === Gift Configurations ===
    gift_api_url = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.api_url",
    )
    gift_api_key = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.api_key",
    )
    gift_api_secret = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.api_secret",
    )

    # === Cardmoola Configurations ===
    cardmoola_api_url = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_url",
    )
    cardmoola_api_key = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_key",
    )
    cardmoola_api_secret = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_secret",
    )

    # === SkipCash Configurations ===
    skipcash_api_url = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.skipcash_api_url",
    )
    skipcash_merchant_key = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.skipcash_merchant_key",
    )
    skipcash_merchant_password = fields.Char(
        readonly=False,
        config_parameter="go_giftcard.skipcash_merchant_password",
    )

    # fetch brand

    brand_country_id = fields.Many2one(
        "res.country",
        string="Brand Country",
        help="Select the country where this brand is registered or primarily operates.",
        config_parameter="go_giftcard.brand_country_id",
    )

    def action_fetch_brands(self):
        res = self.env["ugo2gift.brand"].action_fetch_brand()
        return res