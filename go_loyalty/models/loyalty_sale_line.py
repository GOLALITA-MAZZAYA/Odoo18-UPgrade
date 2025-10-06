from odoo import models, fields, api


class LoyaltySaleLine(models.Model):
    _name = 'loyalty.sale.line'
    _description = 'Loyalty Sale Line'

    sale_id = fields.Many2one(
        'loyalty.sale',
        string='Loyalty Sale'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    name = fields.Char(
        string='Description'
    )
    quantity = fields.Float(
        string='Quantity',
        default=1.0
    )
    price = fields.Float(
        string='Unit Price'
    )
    discount = fields.Float(
        string='Discount (%)',
        default=0.0
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    @api.depends('quantity', 'price', 'discount')
    def _compute_subtotal(self):
        for line in self:
            qty = line.quantity or 0.0
            price = line.price or 0.0
            discount = line.discount or 0.0
            line.subtotal = qty * price * (1 - discount / 100)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.price = self.product_id.list_price or 0.0
            self.name = self.product_id.display_name
