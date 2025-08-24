# noinspection PyStatementEffect
{
    "name": "Go Organization",
    "version": "1.3",
    "sequence": 10,
    "description": """ Extend functionalities related to partner""",
    "category": "Partner",
    "depends": ["contacts", "mail", "website", "base", "product"],
    "author": "Dhiren Narola",
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/res_country.xml",
        "views/res_bank_type.xml",
        "views/merchant_enquiry.xml",
        "views/user_address.xml",
        "views/menuitems.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
