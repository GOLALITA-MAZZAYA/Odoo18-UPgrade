from odoo.exceptions import UserError
from openai import OpenAI, OpenAIError, BadRequestError

from odoo import models, _


class Channel(models.Model):
    _inherit = "discuss.channel"

    def _call_openai(self, prompt_text, partner_name=""):
        try:
            client = self._get_openai_client()
            model_name = self._get_openai_model()

            response = client.responses.create(
                model=model_name,
                temperature=0.6,
                input=prompt_text,
                max_output_tokens=3000,
                top_p=1,
                user=partner_name or None,
            )

            return response.output_text or _("No response from OpenAI.")

        except BadRequestError:
            return _("OpenAI request failed: Missing or invalid input.")

        except OpenAIError:
            return _("OpenAI request failed. Please check your API settings.")

        except Exception:
            return _("OpenAI request failed. Please try again later.")

    def _get_openai_client(self):
        api_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_chatgpt.openapi_api_key")
        )
        return OpenAI(api_key=api_key)

    def _get_openai_model(self):
        model_name = (
            self.env["ir.config_parameter"].sudo().get_param("go_chatgpt.openai_model")
        )
        return model_name

    def _notify_thread(self, message, msg_vals={}, **kwargs):
        rdata = super()._notify_thread(message, msg_vals=msg_vals, **kwargs)

        chatgpt_channel = self.env.ref("go_chatgpt.channel_chatgpt")
        user_chatgpt = self.env.ref("go_chatgpt.user_chatgpt")
        partner_chatgpt = self.env.ref("go_chatgpt.partner_chatgpt")

        author_id = msg_vals.get("author_id")
        prompt = msg_vals.get("body")
        record_name = msg_vals.get("record_name", "")

        if not prompt or author_id == partner_chatgpt.id:
            return rdata

        partner_name = self.env["res.partner"].browse(author_id).name or ""

        should_respond = False
        target_channel = None

        if (
            author_id != partner_chatgpt.id
            and "ChatGPT" in record_name
            and self.channel_type == "chat"
        ):
            should_respond = True
            target_channel = self
        elif (
            author_id != partner_chatgpt.id
            and msg_vals.get("model", "") == "discuss.channel"
            and msg_vals.get("res_id", 0) == chatgpt_channel.id
        ):
            should_respond = True
            target_channel = chatgpt_channel

        if should_respond and target_channel:
            response_text = self._call_openai(prompt, partner_name)
            target_channel.with_user(user_chatgpt).message_post(
                body=response_text,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )

        return rdata
