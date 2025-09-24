# noinspection PyStatementEffect
{
    "name": "Go ChatGPT",
    "version": "18.0.0.0.0",
    "category": "Tools",
    "sequence": 500,
    "summary": "Integrate Odoo with ChatGPT for AI-powered functionalities",
    "license": "OPL-1",
    "author": "Dhiren Narola",
    "depends": [
        "base",
        "mail",
    ],
    "data": [
        "data/discuss_channel_data.xml",
        "data/user_partner_data.xml",
        "views/res_config_settings.xml",
    ],
    "external_dependencies": {"python": ["openai"]},
    "installable": True,
    "auto_install": False,
    "application": True,
}
