from odoo import models, fields, api, _


class LoyaltyRule(models.Model):
    _name = "loyalty.rule"
    _description = "Loyalty Rule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(string="Rule Name", compute="_compute_name", store=True)
    date = fields.Date(string="Date")
    partner_id = fields.Many2one(
        "res.partner",
        string="Associated Partner",
        required=True,
        tracking=True,
    )
    entity = fields.Selection(
        [
            ("merchant", "Merchant"),
            ("organisation", "Organisation"),
            ("employee_vip", "Employee VIP"),
            ("employee_standard", "Employee Standard"),
        ],
        string="Entity Type",
        required=True,
        tracking=True,
        help="Defines which type of entity this rule applies to.",
    )

    reward_point = fields.Float(
        string="Reward Points",
    )
    reward_amount = fields.Float(string="Reward Amount")

    redeem_point = fields.Float(
        string="Redeem Points",
    )
    redeem_amount = fields.Float(string="Redeem Amount")

    in_point_per_currency = fields.Float(
        string="Points per Currency", store=True, compute="_compute_ratio"
    )
    out_point_per_currency = fields.Float(
        string="Points per Currency (Redeem)", store=True, compute="_compute_ratio"
    )

    rule_line_ids = fields.One2many(
        "loyalty.rule.line", "rule_id", string="Extra Discount Lines"
    )

    merchant_rule_ids = fields.One2many(
        "loyalty.rule.merchant", "rule_id", string="Merchant Specific Rules"
    )

    @api.depends("reward_point", "reward_amount", "redeem_point", "redeem_amount")
    def _compute_ratio(self):
        for rule in self:
            rule.in_point_per_currency = rule.reward_point / (rule.reward_amount or 1)
            rule.out_point_per_currency = rule.redeem_amount / (rule.redeem_point or 1)

    @api.depends("partner_id", "entity")
    def _compute_name(self):
        entity_labels = {
            "merchant": "Merchant",
            "organisation": "Organisation",
            "employee_vip": "VIP",
            "employee_standard": "Standard",
        }

        for rule in self:
            partner_name = rule.partner_id.name or ""
            entity_name = entity_labels.get(rule.entity, "")
            rule.name = (
                f"{partner_name} ({entity_name})" if entity_name else partner_name
            )

    def compute_points(self, amount):
        return (
            (self.in_point_per_currency or 0.0) * (amount or 0.0),
            (self.out_point_per_currency or 0.0) * (amount or 0.0),
        )

    def compute_discount(self, points):
        return (
            (points or 0.0) / (self.in_point_per_currency or 1.0),
            (points or 0.0) / (self.out_point_per_currency or 1.0),
        )

    def _get_new_merchant_lines(self):
        if self.entity not in ['employee_standard', 'employee_vip']:
            return []
        existing = self.merchant_rule_ids.mapped('merchant_id').ids
        merchants = self.env['res.partner'].search([('entity_type', '=', 'merchant')])
        return [(0, 0, {
            'reward_amount': self.reward_amount,
            'reward_point': self.reward_point,
            'redeem_amount': self.redeem_amount,
            'redeem_point': self.redeem_point,
            'merchant_id': m.id,
        }) for m in merchants if m.id not in existing]

    def action_update_merchant_rule(self):
        for rule in self:
            new_lines = rule._get_new_merchant_lines()
            if new_lines:
                rule.merchant_rule_ids = new_lines
        return True

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        for rule in rules:
            rule.action_update_merchant_rule()
        return rules
