from odoo import fields, models

class ProductLabel(models.Model):
    _name = 'product.label'
    _description = 'Product Label'

    name = fields.Char(
        required=True,
        translate=True,
        help='Name of the label'
    )

    label_text_color = fields.Char(
        string='Text Color',
        help='Select a Individual HTML Color code (e.g. #ff0000) to display the color of label text.'
    )
    label_color = fields.Char(
        string='Color',
        help='Select a Individual HTML Color code (e.g. #ff0000) to display the color of label.'
    )

    label_option = fields.Selection([
        ('option_1', 'Option 1'),
        ('option_2', 'Option 2'),
        ('option_3', 'Option 3'),
        ('option_4', 'Option 4'),
        ('option_5', 'Option 5')
    ],
        string='Select the Option for label',
        required=True,
        default='option_1',
    )