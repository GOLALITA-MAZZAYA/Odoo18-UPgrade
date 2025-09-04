# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    platform_id = fields.Many2one(
        "res.partner",
        string="Platform",
        domain="[('entity_type', '=', 'platform')]",
        help="Optional platform partner.",
    )

    # Per-slot banner groups (filtered O2M)
    ad_1_ids = fields.One2many(
        "advertisement.banner", "company_id",
        string="Advertisement 1",
        domain=[("slot", "=", "ad_1")],
    )
    ad_2_ids = fields.One2many(
        "advertisement.banner", "company_id",
        string="Advertisement 2",
        domain=[("slot", "=", "ad_2")],
    )
    ad_3_ids = fields.One2many(
        "advertisement.banner", "company_id",
        string="Advertisement 3",
        domain=[("slot", "=", "ad_3")],
    )
