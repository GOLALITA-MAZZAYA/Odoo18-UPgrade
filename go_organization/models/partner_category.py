from odoo import api, fields, models, _


class PartnerCategory(models.Model):
    _name = "partner.category"
    _description = "Partner Category"
    _order = "sequence"
    _parent_name = "parent_id"
    _parent_store = True

    # Core
    name = fields.Char(required=True, translate=False)
    name_ar = fields.Char(string="Name (Arabic)", translate=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10, help="Ordering helper.")
    # color = fields.Integer('Color', default=0)

    # Hierarchy
    parent_id = fields.Many2one("partner.category", string="Parent Category", index=True, ondelete="restrict")
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("partner.category", "parent_id", string="Child Categories")
    # complete_name = fields.Char(string="Complete Name", compute="_compute_complete_name", store=True, index=True)

    # Classification
    is_restro = fields.Boolean(string="Restaurant Category?")
    scope = fields.Selection(
        [
            ("local", "Local"),
            ("global", "Global"),
            ("both", "Local + Global"),
        ],
        default="both",
        required=True,
        help="Where this category is applicable.",
    )
    country_ids = fields.Many2many("res.country", string="Countries Available")

    # Relations
    organisation_ids = fields.Many2many(
        "res.partner",
        "partner_category_org_rel",
        "category_id",
        "partner_id",
        string="Linked Organisations",
        domain=[("entity_type", "=", "organisation")],
        help="Limit or highlight usage for specific organisations (optional).",
    )

    # Media
    image_icon = fields.Image(string="Icon", max_width=256, max_height=256)
    media_attachment_ids = fields.Many2many(
        "ir.attachment",
        "partner_category_media_rel",
        "category_id",
        "attachment_id",
        string="Media",
        help="Optional images/videos instead of maintaining multiple binary image fields.",
    )

    # SQL Constraints
    _sql_constraints = [
        ("category_name_parent_uniq", "unique(name, parent_id)", "Category name must be unique within the same parent."),
    ]