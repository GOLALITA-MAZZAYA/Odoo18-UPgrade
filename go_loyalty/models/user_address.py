from odoo import models, fields, api,_


class UserAddress(models.Model):
    _name = "user.address"
    _description = "User Address"
    _rec_name = "display_name"
    _order = "customer_id, sequence, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Core
    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        index=True,
        ondelete="cascade",
        tracking=True,
        help="Owner of this address.",
    )
    sequence = fields.Integer(default=10, help="Ordering helper per customer.")

    location_name = fields.Char(string="Location Name", required=True, tracking=True)
    location_landmark = fields.Char(string="Landmark")
    zone = fields.Char()
    street_number = fields.Char()
    building_number = fields.Char()
    apartment_number = fields.Char()
    floor = fields.Char()

    # Use floats for geocoordinates (with sane precision)
    lat = fields.Float(string="Latitude", digits=(16, 6))
    long = fields.Float(string="Longitude", digits=(16, 6))

    # Smart display
    display_name = fields.Char(compute="_compute_display_name", store=True)

    _sql_constraints = [
        # Optional: avoid exact duplicates per customer on (name + building + apt + floor)
        (
            "uniq_address_per_customer",
            "unique(customer_id, location_name, building_number, apartment_number, floor)",
            "An address with the same details already exists for this customer.",
        ),
    ]

    # ─────────────────────────────────────────────────────────────────────
    # COMPUTES
    # ─────────────────────────────────────────────────────────────────────
    @api.depends("location_name", "customer_id")
    def _compute_display_name(self):
        for rec in self:
            parts = [rec.location_name or _("Address")]
            if rec.building_number:
                parts.append(_("Bldg %s") % rec.building_number)
            if rec.apartment_number:
                parts.append(_("Apt %s") % rec.apartment_number)
            if rec.floor:
                parts.append(_("Floor %s") % rec.floor)
            label = " • ".join([p for p in parts if p])
            if rec.customer_id:
                label = f"{rec.customer_id.display_name} — {label}"
            rec.display_name = label

    # ─────────────────────────────────────────────────────────────────────
    # CONSTRAINTS
    # ─────────────────────────────────────────────────────────────────────
    @api.constrains("lat", "long")
    def _check_geo_ranges(self):
        for rec in self:
            if rec.lat is not None and (rec.lat < -90 or rec.lat > 90):
                raise ValidationError(_("Latitude must be between -90 and 90."))
            if rec.long is not None and (rec.long < -180 or rec.long > 180):
                raise ValidationError(_("Longitude must be between -180 and 180."))

    # ─────────────────────────────────────────────────────────────────────
    # NORMALIZATION
    # ─────────────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            for k in (
                "location_name",
                "location_landmark",
                "zone",
                "street_number",
                "building_number",
                "apartment_number",
                "floor",
            ):
                if k in vals and isinstance(vals[k], str):
                    vals[k] = vals[k].strip()
        return super().create(vals_list)

    def write(self, vals):
        for k in (
            "location_name",
            "location_landmark",
            "zone",
            "street_number",
            "building_number",
            "apartment_number",
            "floor",
        ):
            if k in vals and isinstance(vals[k], str):
                vals[k] = vals[k].strip()
        return super().write(vals)

    # ─────────────────────────────────────────────────────────────────────
    # SEARCH UX
    # ─────────────────────────────────────────────────────────────────────
    # def name_search(self, name="", args=None, operator="ilike", limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = [
    #             "|",
    #             "|",
    #             ("location_name", operator, name),
    #             ("location_landmark", operator, name),
    #             ("customer_id.name", "ilike", name),
    #         ]
    #     recs = self.search(domain + args, limit=limit)
    #     return recs.name_get()

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.display_name or rec.location_name or _("Address")))
        return res
