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

    moi_secret_key = fields.Char(
        string="MOI Secret Key", config_parameter="moi.secret_key"
    )
    moi_bearer_token = fields.Char(
        string="MOI Bearer Token", config_parameter="moi.bearer_token"
    )
    
    golalta_passcard_username = fields.Char(
        string="Passcard API Username", config_parameter="golalta_passcard_username"
    )
    golalta_passcard_password = fields.Char(
        string="Passcard API Password", config_parameter="golalta_passcard_password"
    )
    golalta_passcard_url = fields.Char(
        string="Passcard API URL", config_parameter="golalta_passcard_url"
    )
