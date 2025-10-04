# noinspection PyStatementEffect
{
    "name": "Go SMS",
    "version": "18.0.0.0.0",
    "category": "Tools",
    "sequence": 500,
    "summary": "Send and manage SMS notifications from Odoo",
    "author": "Dhiren Narola",
    "license": "OPL-1",
    "depends": ["web"],
    "data": [
        "security/ir.model.access.csv",
        "views/sms_config.xml",
        "views/sms_message.xml",
        "views/menuitems.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
