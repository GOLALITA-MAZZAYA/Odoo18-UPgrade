from odoo import models, fields, api

class AdvertisementTracking(models.Model):
    _name = 'advertisement.tracking'
    _description = 'Advertisement Tracking'
    _rec_name = 'tracking_code'
    _order = 'date desc'

    customer_name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    email = fields.Char(required=True)
    phone = fields.Char(required=True)
    tracking_code = fields.Char(required=True)
    date = fields.Datetime(required=True, default=fields.Datetime.now)

