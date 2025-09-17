# noinspection PyStatementEffect
{
    "name": "Go Voucher",
    "version": "18.0.1.0.0",
    "category": "Marketing",
    "sequence": 500,
    "summary": "Create, manage, and redeem discount vouchers with merchant and organisation support in Odoo.",
    "author": "Dhiren Narola",
    "license": "OPL-1",
    "depends": ["go_giftcard", "go_organization", "mail"],
    "data": [
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/discount_voucher.xml",
        "views/skipcash_transaction.xml",
        "views/menuitems.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
