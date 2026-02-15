from odoo import models, fields,api
from werkzeug.urls import url_join

class PartnerCategory(models.Model):
    _name = 'partner.category'
    _description = 'Partner Category'

    name = fields.Char()
    parent_id = fields.Many2one('partner.category', string='Parent Category', index=True, ondelete='cascade')
    name_arabic = fields.Char(string='Name Arabic')
    parent_path = fields.Char(index=True)
    gif_image = fields.Binary("GIF Image" , oldname="x_gif_image")
    # category_id = fields.Many2one('product.public.category')
    image_icon = fields.Binary("Image", max_width=128, max_height=128)
    image2 = fields.Binary("Image 2", oldname="x_image2")
    image3 = fields.Binary("Image 3", oldname="x_image3")
    image4 = fields.Binary("Image 4", oldname="x_image4")

    image_url = fields.Char(compute='_compute_urls')
    image_url_2 = fields.Char(compute='_compute_urls')
    image_url_3 = fields.Char(compute='_compute_urls')
    image_url_4 = fields.Char(compute='_compute_urls')
    global_local = fields.Boolean(string='Local', oldname='x_global_local')
    global_local_global = fields.Boolean(string='Global', oldname='x_global_local_global')
    country_ids_m2m = fields.Many2many('res.country', string='Countries', oldname='x_country_ids_m2m')
    organisation_ids = fields.Many2many(
        'res.partner',
        relation='partner_category_res_partner_rel',
        column1='partner_category_id',
        column2='res_partner_id',
        string='Organisations',
        domain=[('entity_type', '=', 'organisation')],
        oldname='x_organisation_id'
    )

    @api.depends('image_icon')
    def _compute_urls(self):
        web_base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        for category in self:
            images = {
                'image_url': 'image_icon',
                'image_url_2': 'image2',
                'image_url_3': 'image3',
                'image_url_4': 'image4',
            }
            for field_name, image_field in images.items():
                setattr(
                    category,
                    field_name,
                    url_join(web_base_url, f'/go/api/image/{category.id}/{image_field}/partner.category')
                )
