from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class LoyaltyRestaurantCategory(models.Model):
    _name = "loyalty.restaurant.category"
    _inherit = "image.mixin"
    _description = "Restaurant Category"

    name = fields.Char(
        string="Name",
        required=True,
        help="The display name of the restaurant category.",
    )
    name_arabic = fields.Char(
        string="Name (Arabic)", help="Arabic version of the category name."
    )
    complete_name = fields.Char(
        string="Full Category Name",
        compute="_compute_complete_name",
        store=True,
        recursive=True,
    )

    parent_id = fields.Many2one(
        "loyalty.restaurant.category",
        string="Parent Category",
        index=True,
        ondelete="cascade",
        help="The parent category in the hierarchy.",
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many(
        "loyalty.restaurant.category",
        "parent_id",
        string="Subcategories",
        help="Child categories belonging to this category.",
    )

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for category in self:
            category.complete_name = (
                f"{category.parent_id.complete_name} / {category.name}"
                if category.parent_id
                else category.name
            )

    @api.constrains("parent_id")
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(
                _(
                    "You cannot create a recursive category hierarchy. "
                    "Please select a valid parent category."
                )
            )
