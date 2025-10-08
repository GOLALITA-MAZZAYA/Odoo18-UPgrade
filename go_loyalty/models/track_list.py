from odoo import models, fields,api


class TrackList(models.Model):
    _name = "track.list"
    _description = "Customer Track List"

    customer_id = fields.Many2one("res.partner", string="Customer")
    customer_name = fields.Char(string="Customer Name")
    customer_phone = fields.Char(string="Phone")
    customer_email = fields.Char(string="Email")
    track_type = fields.Char(string="Track Type")
    track_value = fields.Char(string="Track Value")
    track_date_time = fields.Datetime(string="Date & Time")
    product_id = fields.Many2one("product.template", string="Product")
    company_id = fields.Many2one("res.company", string="Company")
    merchant_id = fields.Many2one("res.partner", string="Merchant")

    @api.depends("customer_id", "customer_name", "track_type")
    def _compute_display_name(self):
        for record in self:
            name = record.customer_name or (
                record.customer_id.name if record.customer_id else "Unknown"
            )
            track = record.track_type if record.track_type else ""
            parts = [name]
            if track:
                parts.append(track)
            record.display_name = " - ".join(parts)
