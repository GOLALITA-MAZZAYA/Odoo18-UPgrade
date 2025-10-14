# -*- coding: utf-8 -*-
from odoo import models, fields, api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class OrgRegistrationCode(models.Model):
    _name = "org.registration.code"
    _description = "Registration Code"
    _rec_name = "code"

    code = fields.Char()
    partner_id = fields.Many2one("res.partner")
    assign_id = fields.Many2one("res.partner", string="Assign To")
    assigned_on = fields.Datetime()
    vip = fields.Boolean(string="VIP", default=False, oldname="x_vip")
