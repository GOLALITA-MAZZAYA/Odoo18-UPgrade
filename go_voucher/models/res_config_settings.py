from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    skipcash_authorization_key = fields.Char(
        readonly=False,
        string="SkipCash Authorization Key",
        help="Authorization key used for SkipCash API requests.",
        config_parameter="go_voucher.skipcash_authorization_key",
    )

    voucher_email_from = fields.Char(
        string="Voucher Notification Email",
        help="Email address used as the sender for voucher purchase notifications.",
        config_parameter="go_voucher.voucher_email_from",
    )
