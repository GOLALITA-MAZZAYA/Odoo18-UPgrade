from odoo import models, fields, api, _

class LoyaltyPointTransferLine(models.Model):
    _name = 'loyalty.point.transfer.line'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Loyalty Point Transfer Line'

    transfer_id = fields.Many2one(
        'loyalty.point.transfer',
        string='Transfer',
        help='Reference to the parent loyalty point transfer record.'
    )
    name = fields.Char(
        string='Name',
        help='Optional description for this loyalty point transfer line.'
    )
    credit = fields.Integer(
        string='Credit Points',
        help='Number of points credited to the customer or platform.'
    )
    debit = fields.Integer(
        string='Debit Points',
        help='Number of points debited from the customer or platform.'
    )
    date = fields.Datetime(
        string='Transaction Date',
        help='Date and time when the points were transferred.'
    )
    balance = fields.Integer(
        string='Balance',
        compute='_compute_balance',
        store=True,
        help='Net points after applying credit and debit on this line.'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Customer for whom these points are credited or debited.'
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('post', 'Posted'),
            ('cancel', 'Cancelled')
        ],
        string='Status',
        default='draft',
        help='Current status of this loyalty point transfer line.'
    )
    generator_id = fields.Many2one(
        'loyalty.point.generator',
        string='Generated From',
        help='The loyalty point generator that created this transfer line.'
    )
    sale_id = fields.Many2one(
        'loyalty.sale',
        string='Related Sale',
        help='Related sale order linked to this transfer line, if any.'
    )

    @api.depends('credit', 'debit')
    def _compute_balance(self):
        for line in self:
            line.balance = (line.credit or 0) - (line.debit or 0)
