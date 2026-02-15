from odoo import models, fields, api


class SMSConfig(models.Model):
    _name = "sms.config"
    _description = "SMS Configuration"

    user_name = fields.Char(
        string="Username",
        required=True,
        help="Username provided by your SMS service provider.",
    )
    password = fields.Char(
        string="Password",
        required=True,
        help="Password provided by your SMS service provider.",
    )
    smpp_server = fields.Char(
        string="SMPP Server",
        required=True,
        help="The hostname or IP address of the SMS gateway's SMPP server.",
    )
    smpp_port = fields.Integer(
        string="SMPP Port",
        required=True,
        help="The port number used to connect to the SMPP server.",
    )
    url = fields.Char(
        string="URL",
        compute="_compute_url",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.depends("smpp_server")
    def _compute_url(self):
        service_endpoint = "SendSMS"
        for config in self:
            config.url = (
                f"{config.smpp_server.rstrip('/')}/{service_endpoint}"
                if config.smpp_server
                else False
            )

    @api.depends("user_name", "smpp_server")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"{rec.user_name} ({rec.smpp_server})"
                if rec.user_name and rec.smpp_server
                else rec.user_name or rec.smpp_server or "Unnamed"
            )
