# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restaurant_payment_url = fields.Char(
        string="Restaurant Payment URL",
        config_parameter="go_loyalty.payment_url",
        help="Base URL used for initiating restaurant order payments.",
    )

    gulfexc_secret_key = fields.Char(
        string="GulfExc Secret Key", config_parameter="gulfexc.secret_key"
    )
