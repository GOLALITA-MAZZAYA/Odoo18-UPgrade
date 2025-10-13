from odoo import models, fields


class MerchantEnquiry(models.Model):
    _name = "merchant.enquiry"
    _description = "Merchant Enquiry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(
        required=True, tracking=True, help="Requester name or enquiry title."
    )
    phone = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    country = fields.Char(
    )
    city = fields.Char(string="City")

    departure_date = fields.Date(string="Departure Date", tracking=True)
    return_date = fields.Date(string="Return Date", tracking=True)

    hotel_name = fields.Char(string="Preferred Hotel")
    no_adult = fields.Integer(string="Number of Adults", default=1)
    no_children = fields.Integer(string="Number of Children", default=0)

    note = fields.Text(string="Other Information")

    partner_id = fields.Many2one("res.partner", ondelete="cascade")

    product_id = fields.Many2one(
        "product.template", string="Product", oldname="x_product_id"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="partner_id.company_id.currency_id",
        store=True,
        readonly=True,
    )
    product_name = fields.Char(string="Product Name", oldname="x_product_name")
    product_price = fields.Monetary(
        string="Product Price", currency_field="currency_id", oldname="x_product_price"
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        required=True,
    )

    def action_send_mail(self):
        template = self.env.ref(
            "go_loyalty.merchant_enquiry_notification", raise_if_not_found=False
        )
        if not template:
            return False
        for record in self:
            if record.state != "sent":
                template.sudo().send_mail(record.id, force_send=True)
                record.sudo().write({"state": "sent"})
