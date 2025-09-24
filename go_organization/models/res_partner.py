# -*- coding: utf-8 -*-
from datetime import date

from odoo.exceptions import ValidationError

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    # ───────────────────────────────────────────────────────────────────────────
    # Core classification (final list, unchanged names)
    # ───────────────────────────────────────────────────────────────────────────
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

    partner_category_ids = fields.Many2many(
        "partner.category",
        string="Categories",
        help="Optional categorisation for reporting and search.",
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Merchant/Org flags & rating
    # ───────────────────────────────────────────────────────────────────────────
    has_offers = fields.Boolean(string="Has Offers", oldname="x_have_offers")
    has_branches = fields.Boolean(string="Has Branches", oldname="x_have_branch")

    merchant_type = fields.Selection(
        [("standard", "Standard"), ("premium", "Premium")],
        default="standard",
        string="Merchant Tier",
        help="Commercial tier for the merchant.",
    )
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

    is_hotel_business = fields.Boolean(string="Hotel Business", oldname="is_hotel_type")
    is_restaurant = fields.Boolean(string="Restaurant", oldname="is_restro")

    premium_client = fields.Boolean(string="Premium Client")
    client_type = fields.Selection(
        [
            ("standard", "Standard Client"),
            ("premium_local", "Local Premium Client"),
            ("premium_international", "International Premium Client"),
            ("premium_merchant", "Premium Merchant"),
        ],
        string="Client Type",
        oldname="merchant_client_type",
        default="standard",
    )
    local_premium = fields.Boolean(
        string="Local Premium Client", oldname="local_client"
    )
    international_premium = fields.Boolean(
        string="International Premium Client", oldname="int_client"
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Localization / Arabic fields
    # ───────────────────────────────────────────────────────────────────────────
    arabic_name = fields.Char(string="Arabic Name", oldname="x_arabic_name")
    ar_contact_number = fields.Char(
        string="Arabic Contact Number", oldname="x_contact_number_ar"
    )
    ar_email = fields.Char(string="Arabic Email", oldname="x_email_ar")
    ar_street = fields.Char(string="Arabic Street", oldname="x_street_ar")
    ar_city = fields.Char(string="Arabic City", oldname="x_city_ar")
    ar_country = fields.Char(string="Arabic Country", oldname="x_country_ar")
    ar_time_from = fields.Char(string="Arabic Time From", oldname="x_time_from_ar")
    ar_time_to = fields.Char(string="Arabic Time To", oldname="x_time_to_ar")

    # ───────────────────────────────────────────────────────────────────────────
    # Public/website visibility & ribbons
    # ───────────────────────────────────────────────────────────────────────────
    show_in_moi = fields.Boolean(
        string="Show in MOI",
        oldname="x_moi_show",
        help="Expose merchant in MOI channel.",
    )
    hide_from_homepage = fields.Boolean(
        string="Hide on Registration/Homepage", oldname="x_reg_hide"
    )
    online_store = fields.Boolean(string="Online Store", oldname="x_online_store")

    ribbon_text = fields.Char(string="Ribbon Text")
    ribbon_text_ar = fields.Char(
        string="Ribbon Text (Arabic)", oldname="x_ribbon_text_arabic"
    )
    ribbon_color = fields.Char(string="Ribbon Background Color")
    ribbon_mode = fields.Selection(
        [("slanted", "Slanted"), ("tag", "Tag")], default="slanted"
    )
    ribbon_position = fields.Selection(
        [("left", "Left"), ("right", "Right")], default="left"
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Media & content
    # ───────────────────────────────────────────────────────────────────────────
    small_logo = fields.Image(string="Small Logo", oldname="small_logo")
    merchant_banner = fields.Image(string="Merchant Banner")
    map_banner = fields.Image(string="Map Banner", oldname="map_banner")

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

    # ───────────────────────────────────────────────────────────────────────────
    # Contact / device / barcode
    # ───────────────────────────────────────────────────────────────────────────
    device_id = fields.Char(string="Device ID")
    device_token = fields.Char(string="Device Token")
    device_type = fields.Selection(
        [("android", "Android"), ("ios", "iOS")], string="Device Type"
    )
    token_permanent = fields.Boolean(
        string="Permanent Token",
        oldname="x_is_token_permanent",
        help="Only set if confirmed.",
    )
    mobile_version = fields.Char("Mobile Version")

    barcode = fields.Char(
        string="Customer Barcode or Merchant PIN",
        help="Use a barcode to identify this contact.",
    )
    user_expiry_date = fields.Date(
        string="User Expiry", help="Use this Date field; legacy text is migrated here."
    )
    merchant_pin = fields.Char(string="Merchant PIN", oldname="x_merchant_pin_new")

    # ───────────────────────────────────────────────────────────────────────────
    # Merchant operational settings (restaurant/delivery)
    # ───────────────────────────────────────────────────────────────────────────
    accept_delivery = fields.Boolean(
        string="Accept Delivery", oldname="x_accept_delivery"
    )
    open_from = fields.Char(string="Open From", oldname="x_from_open")
    open_till = fields.Char(string="Open Till", oldname="x_open_till")
    order_prep_time = fields.Char(
        string="Order Preparation Time", oldname="x_time_for_order_prepration"
    )
    delivery_cost = fields.Float(string="Delivery Cost", oldname="x_delivery_cost")
    short_description_en = fields.Char(
        string="Short Description (EN)", oldname="x_description"
    )
    short_description_ar = fields.Char(
        string="Short Description (AR)", oldname="x_description_arabic"
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Terms & contract
    # ───────────────────────────────────────────────────────────────────────────
    is_premium_merchant = fields.Boolean(
        string="Is Premium Merchant", oldname="x_is_premium_merchant"
    )
    pdf_attached = fields.Boolean(string="PDF Attached", oldname="x_pdf_attached")

    company_registration = fields.Char()
    company_registration_id = fields.Binary(
        string="Company Registration File",
        help="Company Registration and related files for this partner.",
    )

    company_registration_date = fields.Date(
        string="Company Registration Date", oldname="x_company_registartion_date"
    )
    company_expiry_date = fields.Date(
        string="Company Registration Expiry Date", oldname="x_company_expiry_date"
    )

    contract_expiry = fields.Date(string="Contract Expiry", oldname="x_contract_expiry")
    contract_attachment_ids = fields.Many2many(
        "ir.attachment",
        "res_partner_contract_rel",  # relation table
        "partner_id",
        "attachment_id",
        string="Contract Files",
        help="Contracts and related files for this partner.",
    )

    terms_conditions_en = fields.Html(
        string="Terms & Conditions (EN)", oldname="x_terms_condition_new"
    )
    terms_conditions_ar = fields.Html(
        string="Terms & Conditions (AR)", oldname="x_terms_condition_arabic_new"
    )

    # ───────────────────────────────────────────────────────────────────────────
    # Misc & metrics
    # ───────────────────────────────────────────────────────────────────────────
    organisation_linked_id = fields.Many2one(
        "res.partner",
        string="Organisation Linked With",
        oldname="x_org_linked",
        domain=[("entity_type", "=", "organisation")],  # Only show organisations
    )

    merchant_mobile_visit_count = fields.Integer(
        string="Merchant Mobile App Visits",
        oldname="x_merchant_mobile_count",
        help="No. of times the merchant page was visited from the mobile app.",
    )

    sequence = fields.Integer(string="Sequence #", oldname="x_sequence")
    cc_emails_management = fields.Char(
        string="CC – Management",
        oldname="x_cc_emails_outlet",
        help="Comma-separated emails.",
    )

    from_website = fields.Boolean(string="From Website")
    enable_whatsapp = fields.Boolean(string="Enable WhatsApp")
    whatsapp_title = fields.Char(string="WhatsApp Title")
    whatsapp_number = fields.Char(string="WhatsApp Number")
    whatsapp_prefill_message = fields.Text(string="WhatsApp Prefill Message")

    merchant_page_count = fields.Integer(string="Merchant Page Views", default=0)

    # Lists / relations
    merchant_enquiry_ids = fields.One2many(
        "merchant.enquiry", "partner_id", string="Merchant Enquiries"
    )
    branch_ids = fields.One2many("merchant.branch", "partner_id", string="Branches")
    not_linked_ids = fields.Many2many(
        "notin.app",
        "partner_not_linked_rel",
        "partner_id",
        "not_linked_id",
        string="Not Linked in App",
    )

    # MOI-only misc
    not_in_list = fields.Boolean(string="Not In List", oldname="x_not_in_list")
    moi_last_name = fields.Char(string="MOI Last Name", oldname="x_moi_last_name")

    # Email routing for enquiries
    email_to_send = fields.Char(string="Primary Emails", help="Comma separated emails")
    email_to_cc = fields.Char(string="CC Emails", help="Comma separated emails")

    # Notification group flag
    notification_group = fields.Boolean(
        string="Notification Group", oldname="x_notication_group"
    )

    # Web view
    web_view_customer = fields.Boolean(string="Web View Customer")
    web_view_customer_id = fields.Char(string="Web View Customer ID")

    # ───────────────────────────────────────────────────────────────────────────
    # Organisation: employees limits & counts (VIP/Standard)
    # ───────────────────────────────────────────────────────────────────────────
    employee_type = fields.Selection(
        [("vip", "VIP"), ("standard", "Standard")],
        string="Employee Type",
        help="Category for organisation employees.",
    )
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
    )
    family_head_member_id = fields.Many2one("res.partner", string="Family Head")
    family_member_ids = fields.One2many(
        "res.partner", "family_head_member_id", string="Family Members"
    )

    vip_employee_limit = fields.Integer(string="VIP Employee Limit", default=5)
    standard_employee_limit = fields.Integer(
        string="Standard Employee Limit", default=10
    )
    total_allowed_employee = fields.Integer(
        string="Total Allowed Employees",
    )
    total_registered_employee = fields.Integer(
        string="Total Registered Employees",
        compute="_compute_employee_count",
        store=True,
        readonly=True,
    )
    vip_count = fields.Integer(
        string="VIP Count", compute="_compute_employee_count", store=True, readonly=True
    )
    standard_count = fields.Integer(
        string="Standard Count",
        compute="_compute_employee_count",
        store=True,
        readonly=True,
    )

    # Public image URL for convenience (read-only)
    # image_url = fields.Char(
    #     string="Public Image URL", compute="_compute_url", readonly=True
    # )

    # Org codes / registration windows
    registration_from = fields.Date(string="Registration From")
    registration_to = fields.Date(string="Registration To")
    need_registration_code = fields.Boolean(string="Requires Registration Code")
    # code_ids = fields.One2many("org.registration.code", "partner_id", string="Registration Codes")
    is_expired = fields.Boolean(
        string="Registration Expired", compute="_compute_is_expired", store=True
    )

    # ───────────────────────────────────────────────────────────────────────────
    # COMPUTES
    # ───────────────────────────────────────────────────────────────────────────
    @api.depends("vip_employee_limit", "standard_employee_limit")
    def _compute_total_allowed_employee(self):
        for rec in self:
            rec.total_allowed_employee = (rec.vip_employee_limit or 0) + (
                rec.standard_employee_limit or 0
            )

    @api.depends("child_ids", "child_ids.employee_type", "entity_type")
    def _compute_employee_count(self):
        for rec in self:
            if rec.entity_type != "organisation":
                rec.vip_count = 0
                rec.standard_count = 0
                rec.total_registered_employee = 0
                continue
            vip = sum(1 for c in rec.child_ids if c.employee_type == "vip")
            std = sum(1 for c in rec.child_ids if c.employee_type == "standard")
            rec.vip_count = vip
            rec.standard_count = std
            rec.total_registered_employee = vip + std

    @api.depends("registration_to")
    def _compute_is_expired(self):
        today = date.today()
        for rec in self:
            rec.is_expired = bool(rec.registration_to and rec.registration_to < today)

    # @api.depends("image_1920")
    # def _compute_url(self):
    #     base = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
    #     for rec in self:
    #         rec.image_url = (
    #             url_join(base, f"/go/api/image/{rec.id}/image_512/res.partner")
    #             if rec.id
    #             else False
    #         )

    # ───────────────────────────────────────────────────────────────────────────
    # CONSTRAINTS & ONCHANGES
    # ───────────────────────────────────────────────────────────────────────────
    @api.constrains("enable_whatsapp", "whatsapp_number")
    def _check_whatsapp_number(self):
        for rec in self:
            if rec.enable_whatsapp and not rec.whatsapp_number:
                raise ValidationError(
                    _("WhatsApp number is required when WhatsApp is enabled.")
                )

    @api.constrains(
        "vip_count",
        "standard_count",
        "vip_employee_limit",
        "standard_employee_limit",
        "entity_type",
    )
    def _check_employee_limits(self):
        for rec in self:
            if rec.entity_type == "organisation":
                if rec.vip_count > (rec.vip_employee_limit or 0):
                    raise ValidationError(
                        _("VIP employees (%s) exceed the limit (%s).")
                        % (rec.vip_count, rec.vip_employee_limit or 0)
                    )
                if rec.standard_count > (rec.standard_employee_limit or 0):
                    raise ValidationError(
                        _("Standard employees (%s) exceed the limit (%s).")
                        % (rec.standard_count, rec.standard_employee_limit or 0)
                    )

    @api.onchange("entity_type")
    def _onchange_entity_type_cleanup(self):
        """Optional QoL: clear irrelevant fields when switching type (prevents stale UI)."""
        for rec in self:
            if rec.entity_type != "merchant":
                rec.merchant_type = False
                rec.merchant_rating = False
                rec.is_hotel_business = False
                rec.is_restaurant = False
            if rec.entity_type != "organisation":
                rec.vip_employee_limit = 0
                rec.standard_employee_limit = 0
                rec.total_registered_employee = 0

    # ───────────────────────────────────────────────────────────────────────────
    # Defaults
    # ───────────────────────────────────────────────────────────────────────────
    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        # Keep the legacy behavior: default to Qatar when nothing is set
        if not values.get("country_id"):
            country = self.env["res.country"].search([("code", "=", "QA")], limit=1)
            if country:
                values["country_id"] = country.id
        return values
