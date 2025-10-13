from odoo import models, fields,api
from werkzeug.urls import url_join

class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    name = fields.Char()
    parent_id = fields.Many2one('partner.category', string='Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True)
    category_id = fields.Many2one('product.public.category')
    image_icon = fields.Image("Image", max_width=128, max_height=128)
    image_url = fields.Char(compute='_compute_urls')
    image_url_2 = fields.Char(compute='_compute_urls')
    image_url_3 = fields.Char(compute='_compute_urls')
    image_url_4 = fields.Char(compute='_compute_urls')

    @api.depends('image_icon')
    def _compute_urls(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        for category in self:
            images = {
                'image_url': 'image_icon',
                'image_url_2': 'x_image2',
                'image_url_3': 'x_image3',
                'image_url_4': 'x_image4',
            }
            for field_name, image_field in images.items():
                setattr(
                    category,
                    field_name,
                    url_join(web_base_url, f'/go/api/image/{category.id}/{image_field}/partner.category')
                )
