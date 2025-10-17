from odoo import models, fields, api, _

class OfferUsagesHistory(models.Model):
    _name = 'offer.usages.history'
    _description = 'Offer Usages History'
    _order = 'used_on desc'

    name = fields.Char(string='Reference No.', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    organisation_id = fields.Many2one(
        'res.partner',
        string='Organisation',
        compute='_compute_organisation',
        store=True
    )
    used_on = fields.Datetime(string='Used On', default=fields.Datetime.now, required=True)
    product_id = fields.Many2one('product.template', string='Product', required=True)
    usage_count = fields.Integer(string='Usages Count', default=1, required=True)

    @api.depends('partner_id')
    def _compute_organisation(self):
        for record in self:
            record.organisation_id = record.partner_id.parent_id or False


    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.name = f"OFF00{record.id}"
        return records
