from odoo import models, fields, api


class LoyaltyRuleMerchant(models.Model):
    _name = 'loyalty.rule.merchant'
    _description = 'Merchant-Specific Loyalty Rule'

    merchant_id = fields.Many2one(
        "res.partner",
        string="Merchant",
        domain=[("entity_type", "=", "merchant")],
    )
    rule_id = fields.Many2one(
        'loyalty.rule',
        string='Loyalty Rule'
    )

    partner_id = fields.Many2one(
        'res.partner',
        related='rule_id.partner_id',
        string='Associated Partner',
        store=True
    )
    entity = fields.Selection(
        related='rule_id.entity',
        string='Entity Type',
        store=True
    )

    reward_point = fields.Float(
        string='Reward Points'
    )
    reward_amount = fields.Float(
        string='Reward Amount'
    )
    in_point_per_currency = fields.Float(
        string='In Points per Currency',
        store=True,
        compute='_compute_ratio'
    )

    redeem_point = fields.Float(
        string='Redeem Points'
    )
    redeem_amount = fields.Float(
        string='Redeem Amount'
    )
    out_point_per_currency = fields.Float(
        string='Out Points per Currency',
        store=True,
        compute='_compute_ratio'
    )

    @api.depends("reward_point", "reward_amount", "redeem_point", "redeem_amount")
    def _compute_ratio(self):
        for rule in self:
            reward_amount = rule.reward_amount or 0.0
            redeem_point = rule.redeem_point or 0.0

            rule.in_point_per_currency = (
                (rule.reward_point or 0.0) / reward_amount if reward_amount else 1.0
            )
            rule.out_point_per_currency = (
                (rule.redeem_amount or 0.0) / redeem_point if redeem_point else 1.0
            )

    def compute_points(self, amount):
        amount = amount or 0.0
        return (
            (self.in_point_per_currency or 1.0) * amount,
            (self.out_point_per_currency or 1.0) * amount,
        )

    def compute_discount(self, points):
        points = points or 0.0
        return (
            points / (self.in_point_per_currency or 1.0),
            points / (self.out_point_per_currency or 1.0),
        )
