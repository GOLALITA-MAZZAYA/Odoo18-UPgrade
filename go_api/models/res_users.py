# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    token = fields.Char()

    def get_user_access_token(self):
        self.ensure_one()
        if self.partner_id.is_token_permanent and self.token:
            return self.token
        new_token = uuid.uuid4().hex
        self.sudo().write({"token": new_token})
        return new_token
