import base64

from odoo.exceptions import UserError
from odoo.http import request, route

# import magic
from odoo import _, SUPERUSER_ID, http
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as OAuthSignupHome
from odoo.addons.http_routing.models.ir_http import unslug
from odoo.addons.portal.controllers.portal import CustomerPortal


class AuthSignupHome(OAuthSignupHome):

    def _prepare_signup_values(self, qcontext):
        values = {key: qcontext.get(key) for key in "entity_type"}
        result = super()._prepare_signup_values(qcontext)
        if values.get("entity_type") in ["merchant", "organisation"]:
            result["company_type"] = "company"
        return result


class GoCustomerPortal(CustomerPortal):

    @route(["/my/account"], type="http", auth="user", website=True)
    def account(self, redirect=None, **post):
        partner = request.env.user.partner_id
        values = {}
        if post and request.httprequest.method == "POST":
            image_1920 = post.pop("image_1920")
            ufile = post.pop("ufile")
            error, error_message = self.details_form_validate(post)
            if not error:
                values["image_1920"] = False
                if image_1920:
                    image = image_1920.read()
                    values["image_1920"] = base64.b64encode(image)

                if ufile:
                    f = ufile.read()
                    values["ufile"] = base64.b64encode(f)

                partner.sudo().write(values)
        return super(GoCustomerPortal, self).account(redirect=redirect, **post)
