from odoo import models, fields


class LoyaltyRuleLine(models.Model):
    _name = 'loyalty.rule.line'
    _description = 'Loyalty Rule Line'

    merchant_id = fields.Many2one(
        'res.partner',
        string='Merchant',
        domain=[('entity_type', '=', 'merchant')]
    )
    discount = fields.Float(
        string='Discount'
    )

    rule_id = fields.Many2one(
        'loyalty.rule',
        string='Loyalty Rule'
    )
