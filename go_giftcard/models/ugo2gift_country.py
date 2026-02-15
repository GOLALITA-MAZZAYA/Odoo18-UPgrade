import pytz

from odoo import models, fields


def _tz_get(self):
    _tzs = [
        (tz, tz)
        for tz in sorted(
            pytz.all_timezones, key=lambda tz: tz if not tz.startswith("Etc/") else "_"
        )
    ]
    return _tzs


class Ugo2GiftCountry(models.Model):
    _name = "ugo2gift.country"
    _description = "Ugo2Gift Country"

    name = fields.Char(
        string="Country Name",
        required=True,
        translate=True,
        help="Enter the name of the country.",
    )

    code = fields.Char(
        string="Country Code",
        required=True,
        help="Enter the ISO code or unique code of the country.",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        help="Select the currency used in this country.",
    )

    timezone = fields.Selection(
        selection=_tz_get,
        string="Timezone",
        default=lambda self: self._context.get("tz"),
        help=(
            "When printing documents and exporting/importing data, time values are computed "
            "according to this timezone.\n"
            "If the timezone is not set, UTC (Coordinated Universal Time) is used.\n"
            "Anywhere else, time values are computed according to the time offset of your web client."
        ),
    )

    mobile_number_formats = fields.Char(
        string="Mobile Number Formats",
        help="Specify the mobile number formats for this country, e.g., +971XXXXXXXXX.",
    )

    mobile_number_regex = fields.Char(
        string="Mobile Number Regex",
        help="Regular expression to validate mobile numbers in this country.",
    )

    detail_url = fields.Char(
        string="Detail URL", help="Optional URL to more information about the country."
    )

    languages = fields.One2many(
        "ugo2gift.language",
        "country_id",
        string="Languages",
        help="Languages spoken in this country.",
    )
