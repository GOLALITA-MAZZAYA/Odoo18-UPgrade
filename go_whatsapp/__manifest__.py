{
    "name": "WhatsApp Base Connector",
    "version": "18.0.0.0.0",
    "category": "Communication",
    "sequence": 500,
    "summary": "Base WhatsApp integration with Odoo.",
    "author": "Dhiren Narola",
    "license": "OPL-1",
    "depends": [
        "base",
        'sms',
    ],
    "data": [
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}


