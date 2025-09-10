from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    gift_api_url = fields.Char(
        string="Gift API URL", help="Base URL of the Gift service provider's API."
    )
    gift_api_key = fields.Char(
        string="Gift API Key",
        help="API key provided by the Gift service provider for authentication.",
    )
    gift_api_secret = fields.Char(
        string="Gift API Secret",
        help="Secret key paired with the API key to securely connect with the Gift service.",
    )

    cardmoola_api_url = fields.Char(
        string="Cardmoola API URL",
        help="The base URL of the Cardmoola Gift API used for integration.",
    )
    cardmoola_api_key = fields.Char(
        string="Cardmoola API Key",
        help="The public API key provided by Cardmoola to authenticate requests.",
    )
    cardmoola_api_secret = fields.Char(
        string="Cardmoola API Secret",
        help="The secret key paired with the API key to securely connect with the Cardmoola Gift service.",
    )


    skipcash_api_url = fields.Char(
        string="SkipCash API URL",
        help="Base URL of the SkipCash payment API",
    )
    skipcash_merchant_key = fields.Char(
        string="SkipCash Merchant Key",
        help="Merchant Key provided by SkipCash for authentication.",
    )
    skipcash_merchant_password = fields.Char(
        string="SkipCash Merchant Password",
        help="Merchant Password (secret) provided by SkipCash.",
    )
