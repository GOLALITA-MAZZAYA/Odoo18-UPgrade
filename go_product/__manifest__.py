{
    'name': 'Go Product',
    'version': '18.0.0.0.0',
    'category': 'Product',
    'sequence': 500,
    "summary": "Enhanced the functionalities of product from website side",
    "license": "OPL-1",
    'depends': ["product","website", "sale" ,"mail", "website_sale" ,"account" ,"purchase"],
    'data': [
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/product_brand.xml",
        "views/product_sticker.xml",
        "views/product_label.xml",
        "views/menuitems.xml"
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
