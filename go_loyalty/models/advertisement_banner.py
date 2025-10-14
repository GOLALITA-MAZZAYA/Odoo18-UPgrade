from odoo import models, fields, api


class AdvertisementBanner(models.Model):
    _name = "advertisement.banner"
    _description = "Advertisement Banner"

    name = fields.Char(string="Name")
    banner_image = fields.Binary(string="Banner")
    banner_url = fields.Char(string="Banner URL")
    advertisement = fields.Selection(
        [
            ("ad_1", "Advertisement 1"),
            ("ad_2", "Advertisement 2"),
            ("ad_3", "Advertisement 3"),
        ],
        string="Advertisement",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company"
    )

    android = fields.Boolean(string="Android", oldname="x_android")
    internal = fields.Boolean(string="Internal", oldname="x_internal")
    ios = fields.Boolean(string="iOS", oldname="x_ios")
    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain="[('entity_type', '=', 'merchant')]",
        oldname="x_merchant_id",
    )

    org_type = fields.Selection(
        selection=[
            ("sjc", "SJC"),
            ("gulfexchange", "Gulf Exchange"),
            ("golalita", "Golalita"),
            ("daam", "DAAM"),
            ("qatarinsurance", "Qatar Insurance"),
            ("masrif", "Masrif"),
            ("barwa", "Barwa"),
            ("alzamanexchange", "Alzaman Exchange"),
            ("moi", "MOI"),
            ("qatar_post", "Qatar Post"),
            ("beema", "Beema"),
            ("hayyakam", "Hayyakam"),
            ("qlm", "QLM"),
        ],
        string="Associated Organisation",
        copy=True,
        store=True,
        oldname="x_org_type",
    )

    seq = fields.Integer(string="Sequence",oldname="x_seq")
    sjc = fields.Boolean(string="SJC" , oldname="x_sjc")
    tracking_code = fields.Char(string="Tracking Code", oldname="x_tracking_code")
