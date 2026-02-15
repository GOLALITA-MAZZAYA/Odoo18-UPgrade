# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_api_url = fields.Char(
        string="WhatsApp API URL",
        help="Base URL of the WhatsApp provider API (e.g., https://api.provider.com/)",
        config_parameter="go_whatsapp.whatsapp_api_url",
    )

    whatsapp_api_token = fields.Char(
        string="WhatsApp API Token",
        help="Authentication token provided by your WhatsApp API provider.",
        config_parameter="go_whatsapp.whatsapp_api_token",
    )

    whatsapp_instance_id = fields.Char(
        string="WhatsApp Instance ID",
        help="Unique instance identifier from your WhatsApp API provider, used to route messages.",
        config_parameter="go_whatsapp.whatsapp_instance_id",
    )
