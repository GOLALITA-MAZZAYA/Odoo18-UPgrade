from odoo import models, fields

class OfferLimits(models.Model):
    _name = 'offer.limits'
    _description = 'Offer Limits'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        ondelete='restrict',
        index=True
    )
    product_id = fields.Many2one(
        'product.template',
        string='Product',
        ondelete='cascade',
    )
    frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
    ], string='Frequency')
    number_of_usages = fields.Integer(string='Number of Usages', required=True)

