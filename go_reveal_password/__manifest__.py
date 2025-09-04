# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    "name": "Password Reveal Widget",
    "version": "18.0.1.0.0",
    "summary": "Adds an eye icon to toggle visibility for password-like fields.",
    "category": "Extra Tools",
    "author": "Dhiren Narola",
    "license": "LGPL-3",
    "depends": [
        "web",
        # 'auth_signup'
        # Uncomment this code if you want to show the icon on signup and reset password pages
    ],
    "data": [
        "views/web_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "go_reveal_password/static/src/scss/password_reveal.scss",
            "go_reveal_password/static/src/js/password_reveal.js",
            "go_reveal_password/static/src/js/password_reveal_field.js",
            "go_reveal_password/static/src/xml/password_reveal.xml",
        ],
        "web.assets_frontend": [
            "go_reveal_password/static/src/scss/password_reveal.scss",
            "go_reveal_password/static/src/js/password_toggle_public.js",
        ],
        "web.assets_public": [
            "go_reveal_password/static/src/scss/password_reveal.scss",
            "go_reveal_password/static/src/js/password_toggle_public.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": [
        "static/description/icon.png",
    ],
}
