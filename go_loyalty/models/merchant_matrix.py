from odoo import models, fields

class MerchantMatrix(models.Model):
    _name = 'merchant.matrix'
    _description = 'Merchant Matrix'
    _order = 'create_date desc'

    res_partner_id = fields.Many2one(
        'res.partner',
        string='Merchant',
        required=True,
        help='Merchant associated with this offer or discount tag.'
    )

    discount_tag = fields.Char(
        string='Discount Tag (Ribbon Text)',
        help='Text shown as the ribbon or discount tag for the merchant.'
    )

    discount_tag_arabic = fields.Char(
      oldname='x_discount_tag_arabic',
    )

    organisation_id = fields.Many2many(
        'res.partner',
        'merchant_matrix_res_partner_rel',  # Proper relation table
        'matrix_id',
        'partner_id',
        string='Organisations',
        domain=[('entity_type', '=', 'organisation')],
        help='Organisations this merchant matrix applies to.'
    )
    offer_details = fields.Char(
        string='Offer Details',
        help='Additional details about the offer or promotion.'
    )
    create_date = fields.Datetime(
        string='Creation Date',
        default=fields.Datetime.now,
        readonly=True
    )
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    employee_type = fields.Selection(
        selection=[
            ("vip", "VIP"),
            ("standard", "Standard"),
            ("both", "Both"),
        ],
        string="Employee Type",
        help="Select whether the employee is VIP, Standard, or Both.",
        oldname="x_for_employee_type",
    )
