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