# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AdvertBanner(models.Model):
    _name = "advertisement.banner"
    _description = "Advert Banner"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name, id"

    # BASIC
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, index=True)
    sequence = fields.Integer(default=10, index=True)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        index=True,
    )

    # SLOT (mapped from old 'advertisement')
    slot = fields.Selection(
        [
            ("ad_1", "Advertisement 1"),
            ("ad_2", "Advertisement 2"),
            ("ad_3", "Advertisement 3"),
        ],
        string="Slot",
        required=True,
        tracking=True,
        oldname="advertisement",
    )

    # MEDIA (store in ir.attachment; not on table column)
    image = fields.Binary(
        string="Banner Image",
        oldname="banner_image",
        help="Upload the banner image (stored as attachment).",
    )
    banner_url = fields.Char(string="Target URL", oldname="banner_url")

    # Targeting / metadata
    android = fields.Boolean(string="Android", tracking=True, oldname="x_android")
    ios = fields.Boolean(string="iOS", tracking=True, oldname="x_ios")
    internal = fields.Boolean(string="Internal", tracking=True, oldname="x_internal")

    tracking_code = fields.Char(string="Tracking Code", oldname="x_tracking_code")
    sjc_code = fields.Boolean(string="SJC Code", oldname="x_sjc")

    # Relations
    organisation_id = fields.Many2one(
        "res.partner",
        string="Linked Organisation",
        domain="[('entity_type','=','organisation')]",
        help="Organisation this banner is linked with (optional).",
    )
    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain="[('entity_type','=','merchant')]",
        context="{'default_entity_type': 'merchant'}",
        help="Merchant this banner is linked with (optional).",
    )

    # Chatter convenience
    message_attachment_count = fields.Integer(readonly=True)

    _sql_constraints = [
        (
            "uniq_banner_per_company_slot_name",
            "unique(company_id, slot, name)",
            "Banner name must be unique per company and slot.",
        ),
    ]

    # ── Validations ──────────────────────────────────────────────────────
    @api.constrains("banner_url")
    def _check_banner_url(self):
        for rec in self:
            if rec.banner_url and not (
                rec.banner_url.startswith("http://")
                or rec.banner_url.startswith("https://")
            ):
                raise ValidationError(
                    _("Target URL must start with http:// or https://")
                )
