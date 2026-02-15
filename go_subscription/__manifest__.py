# noinspection PyStatementEffect
{
    "name": "Go Subscription",
    "version": "18.0.0.0.0",
    "category": "Tools",
    "sequence": 500,
    "summary": "Subscription management with discount vouchers, merchants, and user tracking.",
    "author": "Dhiren Narola",
    "license": "OPL-1",
    "depends": [
        "base",
        "mail",
        "go_giftcard",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/subscription_plan.xml",
        "views/subscription_code.xml",
        "views/subscription_history.xml",
        "views/menuitems.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
