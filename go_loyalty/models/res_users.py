# -*- coding: utf-8 -*-
import uuid
from odoo import models, fields,api


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

    @api.model
    def _signup_create_user(self, values):
        user = super()._signup_create_user(values)
        if user and values.get("entity_type") == "employee":
            template = self.env.ref(
                "auth_signup.mail_template_user_signup_account_created",
                raise_if_not_found=False,
            )
            if template:
                template.sudo().send_mail(user.id, force_send=True)
        return user
