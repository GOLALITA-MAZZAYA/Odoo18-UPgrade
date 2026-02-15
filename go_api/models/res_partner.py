from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_token_permanent = fields.Boolean(
        string="Permanent API Token",
        help="If enabled, the user's API token will remain permanent and will not be regenerated automatically.",
    )

    org_type = fields.Selection(
        selection=[
            ("sjc", "SJC"),
            ("gulfexchange", "Gulf Exchange"),
            ("golalita", "Golalita"),
            ("daam", "DAAM"),
            ("qatarinsurance", "Qatar Insurance"),
            ("masrif", "Masrif"),
            ("barwa", "Barwa"),
            ("alzamanexchange", "Alzaman Exchange"),
            ("moi", "MOI"),
            ("qatar_post", "Qatar Post"),
            ("beema", "Beema"),
            ("hayyakam", "Hayyakam"),
            ("qlm", "QLM"),
        ],
        string="Associated Organisation",
        copy=True,
        store=True,
    )

    pause_notification = fields.Boolean()
