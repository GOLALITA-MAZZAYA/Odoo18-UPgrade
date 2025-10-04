from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoyaltyPointGenerator(models.Model):
    _name = 'loyalty.point.generator'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Loyalty Point Generator'

    def _get_default_platform(self):
        return self.env.user.company_id.platform_id

    name = fields.Char(
        string='Reference',
        copy=False,
        help='Unique reference for this loyalty point transaction.'
    )
    date = fields.Datetime(
        string='Transaction Date',
        default=lambda self: fields.Datetime.now(),
        help='The date and time when the loyalty points are generated.'
    )
    points = fields.Integer(
        string='Loyalty Points',
        required=True,
        tracking=True,
        help='Number of loyalty points to be generated for the platform.'
    )
    note = fields.Text(
        string='Notes',
        help='Optional notes or remarks about this loyalty point generation.'
    )
    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('reject', 'Reject')
        ],
        string='Status',
        default='pending',
        tracking=True,
        help='Current status of the loyalty point generation.'
    )
    platform_id = fields.Many2one(
        'res.partner',
        string='Platform',
        domain="[('entity_type', '=', 'platform')]",
        required=True,
        default=_get_default_platform,
        help='Platform to which these loyalty points will be credited.'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible User',
        default=lambda self: self.env.user,
        help='User responsible for creating this loyalty point transaction.'
    )
    line_ids = fields.One2many(
        'loyalty.point.transfer.line',
        'generator_id',
        string='Point Transfer Lines',
        help='Details of loyalty point transfer entries created from this generator.'
    )

    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'
        self.env['loyalty.point.transfer.line'].create({
            'generator_id': self.id,
            'partner_id': self.platform_id.id,
            'credit': self.points,
            'date': fields.Datetime.now(),
            'state': 'post',
            'name': self.name,
        })

    def action_reject(self):
        self.ensure_one()
        self.state = 'reject'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" not in vals or not vals["name"]:
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "loyalty.generator",
                ) or _("New")
        return super().create(vals_list)
