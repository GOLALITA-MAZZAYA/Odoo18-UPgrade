from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    openapi_api_key = fields.Char(
        string="OpenAI API Key",
        help="Your OpenAI API key for ChatGPT integration. Keep it secure.",
        config_parameter="go_chatgpt.openapi_api_key",
    )

    # openai_model = fields.Char(
    #     string="OpenAI Model",
    #     config_parameter="go_chatgpt.openai_model",
    #     help="Enter the model name, e.g., gpt-4o-mini",
    # )

    openai_model = fields.Selection(
        selection=[
            ("gpt-3.5-turbo", "GPT-3.5 Turbo"),
            ("gpt-4", "GPT-4"),
            ("gpt-4o", "GPT-4o"),
            ("gpt-4.1", "GPT-4.1"),
            ("gpt-4o-mini", "GPT-4o Mini"),
            ("gpt-4.1-mini", "GPT-4.1 Mini"),
            ("gpt-5", "GPT-5"),
            ("gpt-5-mini", "GPT-5 Mini"),
            ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            ("gemini-2.5-flash", "Gemini 2.5 Flash"),
            ("gemini-1.5-pro", "Gemini 1.5 Pro"),
            ("gemini-1.5-flash", "Gemini 1.5 Flash"),
        ],
        string="OpenAI Model",
        config_parameter="go_chatgpt.openai_model",
        help="Enter the model name, e.g., gpt-4o-mini",
        default="gpt-4o"
    )
