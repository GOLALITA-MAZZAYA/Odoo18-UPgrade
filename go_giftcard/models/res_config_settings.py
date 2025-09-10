from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # === Gift Configurations ===
    gift_api_url = fields.Char(
        related="company_id.gift_api_url",
        readonly=False,
        config_parameter="go_giftcard.api_url",
    )
    gift_api_key = fields.Char(
        related="company_id.gift_api_key",
        readonly=False,
        config_parameter="go_giftcard.api_key",
    )
    gift_api_secret = fields.Char(
        related="company_id.gift_api_secret",
        readonly=False,
        config_parameter="go_giftcard.api_secret",
    )

    # === Cardmoola Configurations ===
    cardmoola_api_url = fields.Char(
        related="company_id.cardmoola_api_url",
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_url",
    )
    cardmoola_api_key = fields.Char(
        related="company_id.cardmoola_api_key",
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_key",
    )
    cardmoola_api_secret = fields.Char(
        related="company_id.cardmoola_api_secret",
        readonly=False,
        config_parameter="go_giftcard.cardmoola_api_secret",
    )

    # === SkipCash Configurations ===
    skipcash_api_url = fields.Char(
        related="company_id.skipcash_api_url",
        readonly=False,
        config_parameter="go_giftcard.skipcash_api_url",
    )
    skipcash_merchant_key = fields.Char(
        related="company_id.skipcash_merchant_key",
        readonly=False,
        config_parameter="go_giftcard.skipcash_merchant_key",
    )
    skipcash_merchant_password = fields.Char(
        related="company_id.skipcash_merchant_password",
        readonly=False,
        config_parameter="go_giftcard.skipcash_merchant_password",
    )
