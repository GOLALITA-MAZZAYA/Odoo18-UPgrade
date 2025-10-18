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

    rule_id = fields.Many2one("loyalty.rule", string="Loyalty Rule")
    ad_1_ids = fields.One2many(
        "advertisement.banner", "company_id", domain=[("advertisement", "=", "ad_1")]
    )
    ad_2_ids = fields.One2many(
        "advertisement.banner", "company_id", domain=[("advertisement", "=", "ad_2")]
    )
    ad_3_ids = fields.One2many(
        "advertisement.banner", "company_id", domain=[("advertisement", "=", "ad_3")]
    )


