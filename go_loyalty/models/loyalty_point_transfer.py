from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LoyaltyPointTransfer(models.Model):
    _name = 'loyalty.point.transfer'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Loyalty Point Transfer'

    name = fields.Char(
        string='Reference',
        help='Unique reference for this loyalty point transfer.'
    )
    note = fields.Text(
        string='Notes',
        help='Additional notes regarding this loyalty point transfer.'
    )
    date = fields.Datetime(
        string='Transaction Date',
        default=fields.Datetime.now,
        required=True,
        help='Date and time when the loyalty points transfer was created.'
    )
    from_id = fields.Many2one(
        'res.partner',
        string='From',
        tracking=10,
        required=True,
        help='The partner who is sending the loyalty points.'
    )
    entity_type = fields.Selection(
        related='from_id.entity_type',
        store=True,
        readonly=True,
        string='Sender Entity',
    )
    to_id = fields.Many2one(
        'res.partner',
        string='To',
        tracking=10,
        required=True,
        help='The partner who will receive the loyalty points.'
    )
    points = fields.Integer(
        string='Points to Transfer',
        tracking=20,
        required=True,
        help='Number of loyalty points to transfer.'
    )
    available_points_from = fields.Integer(
        related='from_id.points',
        string='Available Points (Sender)',
        help='The current available points of the sender.'
    )
    available_points_to = fields.Integer(
        related='to_id.points',
        string='Available Points (Receiver)',
        help='The current available points of the receiver.'
    )
    # amount = fields.Float(
    #     string='Amount to Receive',
    #     compute='_compute_amount',
    #     store=True,
    #     help='Equivalent amount of points to receive in currency or value.'
    # )
    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('transfer', 'Transferred'),
            ('cancel', 'Cancelled')
        ],
        string='Status',
        default='pending',
        tracking=20,
        help='Current status of the loyalty point transfer.'
    )
    approval_status = fields.Selection(
        [
            ('sent', 'Sent for Approval'),
            ('approved', 'Approved'),
            ('reject', 'Rejected')
        ],
        string='Approval Status',
        help='Approval status for the transfer if required.'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user.id,
        help='User responsible for this loyalty point transfer.'
    )
    line_ids = fields.One2many(
        'loyalty.point.transfer.line',
        'transfer_id',
        string='Transfer Lines',
        help='Detailed lines of the loyalty points being transferred.'
    )
    # rule_id = fields.Many2one(
    #     'loyalty.rule',
    #     string='Points Redemption Rule',
    #     help='Rule applied for this points transfer, if any.'
    # )
    go_transaction = fields.Boolean(
        string='GO Transaction',
        help='Indicates whether this transfer is a GO transaction.'
    )
    transaction_type = fields.Selection(
        [('sent', 'Sent'), ('receive', 'Receive')],
        string='Transaction Type',
        help='Type of the points transfer: Sent or Received.'
    )

    # @api.depends("rule_id", "points", "to_id", "transaction_type")
    # def _compute_amount(self):
    #     for record in self:
    #         if not record.rule_id:
    #             record.amount = 0
    #             continue
    #
    #         if record.to_id.go_entity == "merchant":
    #             rule = record.rule_id.merchant_rule_ids.filtered(
    #                 lambda m: m.merchant_id == record.to_id
    #             )
    #             rule_to_use = rule or record.rule_id
    #         else:
    #             rule_to_use = record.rule_id
    #
    #         amount_in, amount_out = rule_to_use.compute_discount(record.points)
    #         record.amount = (
    #             amount_out if record.transaction_type == "sent" else amount_in
    #         )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "name" not in vals or not vals["name"]:
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "loyalty.transfer"
                ) or _("New")
        return super(LoyaltyPointTransfer, self).create(vals_list)

    @api.constrains("points")
    def _check_points(self):
        for record in self:
            if record.available_points_from < record.points:
                raise UserError(
                    _(f"You can only transfer {record.available_points_from} points.")
                )

    def action_send_approval_request(self):
        self.approval_status = 'sent'

    def action_cancel(self):
        self.ensure_one()
        self.state = "cancel"

    def action_transfer(self):
        self.ensure_one()
        self.state = 'transfer'

        now = fields.Datetime.now()

        lines = [
            {
                'transfer_id': self.id,
                'debit': self.points,
                'date': now,
                'state': 'post',
                'partner_id': self.from_id.id,
                'name': self.name,
            },
            {
                'transfer_id': self.id,
                'credit': self.points,
                'date': now,
                'state': 'post',
                'partner_id': self.to_id.id,
                'name': self.name,
            },
        ]

        self.env['loyalty.point.transfer.line'].create(lines)

        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Successfully Transferred',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        user = self.env.user
        txn_type = res.get("transaction_type")

        if txn_type == "sent":
            res.update(
                {
                    "from_id": user.partner_id.id,
                    "to_id": user.company_id.platform_id.id,
                    # "rule_id": user.partner_id.rule_id.id,
                }
            )
        elif txn_type == "receive":
            res.update(
                {
                    "from_id": user.company_id.platform_id.id,
                    "to_id": user.partner_id.id,
                    # "rule_id": user.partner_id.rule_id.id,
                }
            )
        elif user.has_group("base.group_system"):
            res.update({"from_id": user.company_id.platform_id.id})

        return res
