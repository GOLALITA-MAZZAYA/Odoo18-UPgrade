from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    points = fields.Integer(
        string="Loyalty Points", compute="_compute_points", store=True
    )

    line_ids = fields.One2many("loyalty.point.transfer.line", "partner_id")

    is_token_permanent = fields.Boolean(
        string="Permanent API Token",
        help="If enabled, the user's API token will remain permanent and will not be regenerated automatically.",
    )

    from_website = fields.Boolean()

    entity_type = fields.Selection(
        [
            ("platform", "Platform"),
            ("organisation", "Organisation"),
            ("merchant", "Merchant"),
            ("employee", "Employee"),
            ("family", "Family Member"),
        ],
        string="Entity Type",
        oldname="go_entity",
        index=True,
        required=True,
        help="Functional role of the contact in your program.",
    )

    phone_verified = fields.Boolean()
    premium_client = fields.Boolean(string="Premium Client", index=True)

    moi_last_name = fields.Char(oldname="x_moi_last_name")
    family_head_member_id = fields.Many2one("res.partner", index=True)

    org_type = fields.Selection(
        selection=[
            ("sjc", "SJC"),
            ("gulfexchange", "Gulf Exchange"),
            ("golalita", "Golalita"),
            ("daam", "DAAM"),
            ("qatarinsurance", "Qatar Insurance"),
            ("masrif", "Masrif"),
            ("barwa", "Barwa"),
            ("alzamanexchange", "Alzaman Exchange"),
            ("moi", "MOI"),
            ("qatar_post", "Qatar Post"),
            ("beema", "Beema"),
            ("hayyakam", "Hayyakam"),
            ("qlm", "QLM"),
        ],
        string="Associated Organisation",
        copy=True,
        store=True,
        oldname="x_org_type",
        index=True,
    )

    user_expiry = fields.Date(oldname="x_user_expiry")

    relation_type = fields.Selection(
        [
            ("sister", "Sister"),
            ("daughter", "Daughter"),
            ("father", "Father"),
            ("mother", "Mother"),
            ("wife", "Wife"),
            ("brother", "Brother"),
            ("son", "Son"),
        ],
        string="Relation Type",
        index=True,
    )

    employee_type = fields.Selection(
        selection=[
            ("vip", "VIP"),
            ("standard", "Standard"),
            ("both", "Both"),
        ],
        string="Employee Type",
        help="Select whether the employee is VIP, Standard, or Both.",
        oldname="x_for_employee_type",
        index=True,
    )

    arabic_name = fields.Char(string="Arabic Name", oldname="x_arabic_name")

    open_from = fields.Datetime(string="Restro Open From", oldname="x_open_from")
    open_till = fields.Datetime(string="Restro Open Till", oldname="x_open_till")
    ribbon_text = fields.Char(string="Ribbon Text")
    ribbon_text_ar = fields.Char(
        string="Ribbon Text (Arabic)", oldname="x_ribbon_text_arabic"
    )

    ribbon_color = fields.Char(string="Ribbon Background Color")
    ribbon_position = fields.Selection(
        [("left", "Left"), ("right", "Right")], default="left"
    )

    merchant_details_en = fields.Html(
        string="Merchant Details (EN)", oldname="merchant_details"
    )
    merchant_details_ar = fields.Html(
        string="Merchant Details (AR)", oldname="x_merchant_details_ar"
    )
    merchant_details_moi_en = fields.Html(
        string="Merchant Details (MOI EN)", oldname="x_merchant_details_moi"
    )
    merchant_details_moi_ar = fields.Html(
        string="Merchant Details (MOI AR)", oldname="x_merchant_details__moi_ar"
    )
    merchant_details_masrif_en = fields.Html(
        string="Merchant Details (Masrif EN)", oldname="x_merchant_details_masrif"
    )
    merchant_details_masrif_ar = fields.Html(
        string="Merchant Details (Masrif AR)", oldname="x_merchant_details_masrif_ar"
    )

    go_loyalty_point = fields.Boolean(
        string="Accept Go Loyalty Point ?",
        help="Select True if this merchant accept Go Loyalty Points",
        oldname="x_go_loyalty_point",
    )

    image_url = fields.Char()

    terms_condition = fields.Text(oldname="x_terms_condition")
    terms_condition_arabic = fields.Text(oldname="x_terms_condition_arabic")

    terms_conditions_en = fields.Html(
        string="Terms & Conditions (EN)", oldname="x_terms_condition_new"
    )

    terms_conditions_ar = fields.Html(
        string="Terms & Conditions (AR)", oldname="x_terms_condition_arabic_new"
    )

    ar_contact_number = fields.Char(
        string="Arabic Contact Number", oldname="x_contact_number_ar"
    )
    show_in_moi = fields.Boolean(
        string="Show in MOI",
        oldname="x_moi_show",
        help="Expose merchant in MOI channel.",
    )

    ar_email = fields.Char(string="Arabic Email", oldname="x_email_ar")
    ar_street = fields.Char(string="Arabic Street", oldname="x_street_ar")
    ar_city = fields.Char(string="Arabic City", oldname="x_city_ar")
    ar_country = fields.Char(string="Arabic Country", oldname="x_country_ar")
    ar_time_from = fields.Char(string="Arabic Time From", oldname="x_time_from_ar")
    ar_time_to = fields.Char(string="Arabic Time To", oldname="x_time_to_ar")
    sequence = fields.Integer(oldname="x_sequence")

    online_store = fields.Boolean(string="Online Store", oldname="x_online_store")

    merchant_rating = fields.Selection(
        [
            ("1", "Bad"),
            ("2", "Average"),
            ("3", "Good"),
            ("4", "Very Good"),
            ("5", "Excellent"),
        ],
        string="Merchant Rating",
        default="4",
        help="Internal quality score.",
    )

    partner_category_id = fields.Many2one("partner.category")
    arabic_name = fields.Char(string="Arabic Name", oldname="x_arabic_name")

    points_earn = fields.Integer()
    points_used = fields.Integer()
    points_values = fields.Integer()
    enable_whatsapp = fields.Boolean(string="Enable WhatsApp Notifications")
    whatsapp_title = fields.Char(string="WhatsApp Title")
    whatsapp_number = fields.Char(string="WhatsApp Number")
    email_verified = fields.Boolean(string="Email Verified")
    whatsapp_prefill_message = fields.Text(string="WhatsApp Prefill Message")

    family_member_ids = fields.One2many('res.partner', 'family_head_member_id')
    pdf_attached = fields.Boolean(string="PDF Attached", oldname="x_pdf_attached")
    is_hotel_type = fields.Boolean(string="Is Hotel Type")
    kts = fields.Char(string="KTS", oldname="x_kts", help="	If Hostel belongs to KTS?")

    mobile_version = fields.Char(string="Mobile Version")

    comment = fields.Text()
    is_published = fields.Boolean(string="Is Published", default=False)
    is_restro = fields.Boolean(string="Is Restaurant")
    merchant_type = fields.Selection(
        [("standard", "Standard"), ("premium", "Premium")],
        default="standard",
        index=True,
    )
    need_registration_code = fields.Boolean(string="Requires Registration Code")
    reg_hide = fields.Boolean(string="Hide Registration Code", oldname="x_reg_hide")
    map_banner = fields.Binary(string="Map Banner")

    code_ids = fields.One2many(
        "org.registration.code", "partner_id", string="Registration Codes"
    )

    pause_notification = fields.Boolean()
    merchant_pin_new = fields.Char(oldname="x_merchant_pin_new")

    contract_copy = fields.Binary(
        string="Contract Copy", oldname="x_contract_copy", attachment=True
    )
    contract_filename = fields.Char(string="Contract Filename")

    company_registartion = fields.Binary(
        string="Company Registration", oldname="x_company_registration", attachment=True
    )
    company_registartion_filename = fields.Char(string="Company Registration Filename")

    is_premium_merchant = fields.Boolean(
        string="Is Premium Merchant", oldname="x_is_premium_merchant"
    )

    cc_emails_outlet = fields.Char(string="CC To Management", oldname="x_cc_emails_outlet")
    go_loyalty_point = fields.Boolean(oldname="x_go_loyalty_point")
    location_id = fields.Many2one("custom.location")

    not_linked_ids = fields.Many2many(
        "notin.app",
        "partner_not_linked_rel",
        "partner_id",
        "not_linked_id",
        string="Not Linked APP",
    )

    not_in_list = fields.Boolean(string="Not in List", oldname="x_not_in_list")

    def _is_registred(self, code):
        return code in self.code_ids.filtered(lambda l: l.assign_id).mapped("code")

    @api.depends("line_ids.partner_id", "line_ids.balance")
    def _compute_points(self):
        for p in self:
            p.points = sum(l.balance for l in p.line_ids)

    def _get_rule(self):
        Rule = self.env["loyalty.rule"]
        entity_map = {
            "organisation": "organisation",
            "merchant": "merchant",
            "employee_standard": "employee_standard",
            "employee_vip": "employee_vip",
        }

        if self.entity_type in ["organisation", "merchant"]:
            entity = entity_map[self.entity_type]
            partner = self
        elif self.entity_type == "employee":
            entity = entity_map[f"employee_{self.employee_type}"]
            partner = self.parent_id
        else:
            return Rule

        return Rule.search(
            [("entity", "=", entity), ("partner_id", "=", partner.id)], limit=1
        )
