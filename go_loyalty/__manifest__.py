# noinspection PyStatementEffect
{
    "name": "Loyalty System",
    "version": "18.0.0.0.0",
    "category": "Tools",
    "summary": "Comprehensive Loyalty Management for Customers and Rewards.",
    "author": "Dhiren Narola",
    "license": "OPL-1",
    "depends": [
        "base",
        "product",
        "account",
        "mail",
        "go_organization"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/loyalty_restaurant_order.xml",
        "views/loyalty_restaurant_category.xml",
        "views/user_address.xml",
        "views/loyalty_point_generator.xml",
        "views/loyalty_point_transfer.xml",
        "views/menus.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
