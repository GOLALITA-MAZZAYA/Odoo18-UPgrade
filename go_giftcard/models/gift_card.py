import base64
import logging
import uuid
from datetime import datetime

from Crypto.Hash import HMAC, SHA256
from httpsig.requests_auth import HTTPSignatureAuth
from odoo.exceptions import ValidationError

from odoo import api, fields, models
from .ugo2gift_api_request import Ugo2GiftAPI

_logger = logging.getLogger(__name__)


class GiftCard(models.Model):
    _name = "gift.card"
    _description = "Gift Card"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        ("reference_unique", "unique(name)", "Gift card reference must be unique.")
    ]

    # === Identifiers ===
    name = fields.Char(
        string="Reference",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code(
            "go_giftcard.gift_card"
        ),
        help="Unique reference number for this gift card, generated automatically.",
    )
    reference_id = fields.Char(
        string="Mobile Reference",
        help="Reference from mobile application or external system.",
    )

    # === Core Details ===

    brand_code = fields.Char(
        string="Brand Code",
        help="The brand associated with this gift card.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        help="Currency in which the gift card amount is defined.",
    )

    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        help="Monetary value of the gift card.",
    )

    country_id = fields.Many2one(
        "res.country",
        help="Country where this gift card can be redeemed.",
    )

    amount_org = fields.Monetary(
        string="Original Amount",
        oldname="x_amount_org",
        currency_field="currency_org_id",
        help="The original amount assigned to this gift card.",
    )

    currency_org_id = fields.Many2one(
        "res.currency",
        string="Original Currency",
        oldname="x_currency_org",
        help="The currency in which the gift card was originally issued.",
    )

    cardmoola_product_id = fields.Char(
        string="CardMoola Product ID",
        oldname="x_product_id",
        help="The product related to this gift card.",
    )

    # === Receiver Info ===

    receiver_name = fields.Char(
        string="Receiver Name", help="Full name of the gift card recipient."
    )
    receiver_email = fields.Char(
        string="Receiver Email", help="Email address of the recipient."
    )
    receiver_phone = fields.Char(
        string="Receiver Phone", help="Phone number of the recipient."
    )
    message = fields.Text(
        string="Message",
        translate=True,
        help="Personalized message for the gift card recipient.",
    )

    # === Customer Info ===

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        help="Customer who purchased or owns this gift card.",
    )

    # === Delivery ===
    delivery_language_id = fields.Many2one(
        "res.lang",
        string="Delivery Language",
        help="Preferred language for delivering this gift card.",
    )
    egift_card_url = fields.Char(
        string="eGift Card URL", help="Link to access the electronic gift card."
    )
    gift_verification_pin = fields.Char(
        string="Gift Verification PIN",
        help="PIN required to redeem the gift card, if applicable.",
    )
    barcode = fields.Char(
        string="Barcode", help="Barcode identifier for scanning and redemption."
    )
    expiry_date = fields.Date(
        string="Expiry Date", help="Expiration date of this gift card."
    )
    redemption_instructions = fields.Text(
        string="Redemption Instructions",
        translate=True,
        help="Steps or guidelines for redeeming this gift card.",
    )

    # === Payment Info ===

    order_id = fields.Char(
        string="Order ID",
        oldname="x_order_id",
        help="The external order reference linked to this gift card.",
    )

    payment_id = fields.Char(
        string="Payment ID", help="Reference ID from the payment gateway."
    )
    payment_status = fields.Char("Payment Status")
    vis_id = fields.Char(
        string="Visa ID",
        help="External system reference for Visa integration (if applicable).",
    )
    payment_web_link = fields.Char(
        string="Payment Link", help="Web link for payment or customer redirection."
    )

    # === System Info ===
    state = fields.Selection(
        [
            ("pending_payment", "Pending Payment"),
            ("paid", "Paid"),
            ("confirmed", "Confirmed"),
            ("delivered", "Delivered"),
        ],
        string="Payment Status",
        default="pending_payment",
        tracking=True,
        readonly=True,
        help="Lifecycle status of the gift card.",
    )
    date_added = fields.Datetime(
        string="Date Added",
        default=fields.Datetime.now,
        help="Date and time when the gift card was created.",
    )

    notify = fields.Boolean(
        string="Notify", help="Enable to notify the receiver about this gift card."
    )

    is_cardmoola = fields.Boolean(
        string="CardMoola",
        oldname="x_is_cardmoola",
        help="Indicates whether this gift card is associated with CardMoola.",
    )

    return_url = fields.Text(
        string="Return URL",
        oldname="x_return_url",
        help="The callback or return URL to redirect after processing the gift card.",
    )

    active = fields.Boolean(string="Active", default=True)

    # Used from Go Voucher
    def create_order(self):
        self.ensure_one()
        api_url, api_key, api_secret = self._check_api_credentials()

        payload = {
            "reference_id": self.reference_id,
            "notify": 1,
            "brand_code": self.brand_code,
            "currency": self.currency_id.name,
            "amount": self.amount,
            "country": self.country_id.name,
            "receiver_name": self.receiver_name,
            "receiver_email": self.receiver_email,
            "receiver_phone": self.receiver_phone,
            "message": self.message,
            "delivery_language": "en",
        }

        headers = {
            "Accept": "application/json",
            "X-Api-Key": api_key,
            "date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        }

        auth = HTTPSignatureAuth(
            key_id=api_key, secret=api_secret, headers=["accept", "date"]
        )

        gift_api = Ugo2GiftAPI(self.env, api_url, api_key, api_secret, headers)
        response = gift_api.create_gift_order(payload, auth=auth)

        if not response.get("success"):
            error_msg = response.get("error") or "Unknown error from gift API"
            gift_api.post_message(f"Warning: Failed to create gift order. {error_msg}")
            return False

        order_data = response.get("data") or {}

        self.write(
            {
                "order_id": order_data.get("order_id") or False,
                "gift_verification_pin": order_data.get("egift_card", {}).get(
                    "gift_verification_pin"
                )
                or False,
                "egift_card_url": order_data.get("egift_card", {}).get("url") or False,
                "redemption_instructions": order_data.get("redemption_instructions")
                or False,
                "barcode": order_data.get("barcode") or False,
                "expiry_date": order_data.get("expiry_date") or False,
            }
        )

        return True

    def marked_paid(self):
        self.write({"state": "paid"})

    def _check_api_credentials(self):

        api_url = (
            self.env["ir.config_parameter"].sudo().get_param("go_giftcard.api_url")
        )
        api_key = (
            self.env["ir.config_parameter"].sudo().get_param("go_giftcard.api_key")
        )
        api_secret = (
            self.env["ir.config_parameter"].sudo().get_param("go_giftcard.api_secret")
        )

        missing_params = []
        if not api_url:
            missing_params.append("Gift API URL")
        if not api_key:
            missing_params.append("Gift API Key")
        if not api_secret:
            missing_params.append("Gift API Secret")

        if missing_params:
            raise ValidationError(
                f"Please configure the following settings before "
                f"syncing brands: {', '.join(missing_params)}"
            )

        return api_url, api_key, api_secret

    # Used from Go Voucher
    def create_cardmoola_order(self):
        self.ensure_one()
        api_url, api_key, api_secret = self._check_cardmoola_api_credentials()

        cardmoola_api = Ugo2GiftAPI(self.env, api_url, api_key, api_secret)

        token = cardmoola_api.get_token("/auth/token")

        if not token:
            return False

        if not token:
            cardmoola_api.post_message("Failed to generate CardMoola token.")
            return False

        order_response = self._prepare_and_send_cardmoola_order(
            token, api_url, api_key, api_secret
        )

        if not order_response.get("success"):
            cardmoola_api.post_message("Failed to create CardMoola order.")
            return False

        order_data = order_response.get("data", {})
        if isinstance(order_data, dict):
            order_summary = order_data.get("data", {}).get("orderSummary", {})

        if not order_summary or order_summary.get("status") != "COMPLETE":
            _logger.error(f"Order creation failed: {order_summary}")
            return False

        order_id = order_summary.get("orderId")
        items = order_summary.get("items", [])

        if items:
            item = items[0] or {}
            recipients = item.get("recipients") or [{}]

            claim_link = recipients[0].get("claimLink") if recipients else None
            photo = item.get("photo") or ""
            description = item.get("description") or ""

            self.write(
                {
                    "order_id": order_id or "",
                    "egift_card_url": claim_link or "",
                    "redemption_instructions": description or "",
                    "gift_verification_pin": photo or "",
                }
            )

    # Used from Go Voucher
    def _prepare_and_send_cardmoola_order(self, token, api_url, api_key, api_secret):
        self.ensure_one()

        missing_fields = []
        if not self.cardmoola_product_id:
            missing_fields.append("CardMoola Product ID")
        if not self.receiver_email:
            missing_fields.append("Receiver Email")
        if not self.receiver_name:
            missing_fields.append("Receiver Name")

        if missing_fields:
            raise ValidationError(
                f"The following fields are required to create a CardMoola order: "
                f"{', '.join(missing_fields)}"
            )

        receiver_name_parts = (self.receiver_name or "").strip().split(" ", 1)
        first_name = receiver_name_parts[0] if receiver_name_parts else ""
        last_name = receiver_name_parts[1] if len(receiver_name_parts) > 1 else ""

        order_payload = {
            "items": [
                {
                    "productId": self.cardmoola_product_id,
                    "price": self.amount,
                    "recipients": [
                        {
                            "email": self.receiver_email,
                            "firstName": first_name,
                            "lastName": last_name,
                        }
                    ],
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        cardmoola_api = Ugo2GiftAPI(self.env, api_url, api_key, api_secret, headers)

        order_response = cardmoola_api.post_cardmoola_order(payload=order_payload)

        return order_response

    # Used from Go Voucher
    def _check_cardmoola_api_credentials(self):

        api_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.cardmoola_api_url")
        )
        api_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.cardmoola_api_key")
        )
        api_secret = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.cardmoola_api_secret")
        )

        missing_params = []
        if not api_url:
            missing_params.append("Cardmoola API URL")
        if not api_key:
            missing_params.append("Cardmoola API Key")
        if not api_secret:
            missing_params.append("Cardmoola API Secret")

        if missing_params:
            raise ValidationError(
                f"Please configure the following settings "
                f": {', '.join(missing_params)}"
            )

        return api_url, api_key, api_secret

    def hash_hmac(self, data, key, raw_output=False):
        hmac_obj = HMAC.new(
            key.encode("utf-8"), msg=data.encode("utf-8"), digestmod=SHA256
        )
        return hmac_obj.digest() if raw_output else hmac_obj.hexdigest()

    def get_skipcash_url(self):
        api_url, merchant_key, merchant_password = (
            self._check_skipcash_api_credentials()
        )
        uid = str(uuid.uuid4())
        self._check_skipcash_required_fields()

        payload = {
            "Uid": uid,
            "KeyId": merchant_key,
            "Amount": str(self.amount),
            "FirstName": self.receiver_name,
            "LastName": self.receiver_name,
            "Email": self.receiver_email,
            "TransactionId": self.reference_id,
            "ReturnUrl": self.return_url or "",
        }

        # Exclude ReturnUrl from signing
        signing_fields = {k: v for k, v in payload.items() if k != "ReturnUrl"}
        signing_string = ",".join(f"{k}={v}" for k, v in signing_fields.items())
        signature = self.hash_hmac(signing_string, merchant_password, raw_output=True)
        authorization = base64.b64encode(signature).decode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }

        skipcash_api = Ugo2GiftAPI(
            self.env, api_url, merchant_key, merchant_password, headers=headers
        )

        response = skipcash_api.create_skipcash_payment(payload)

        if response.get("success"):
            result_obj = response.get("data", {}).get("resultObj", {})
            return {
                "id": result_obj.get("id"),
                "pay_url": result_obj.get("payUrl"),
            }

        return {}

    def _check_skipcash_required_fields(self):
        missing_fields = []
        if not self.amount or self.amount <= 0:
            missing_fields.append("Amount")
        if not self.receiver_name:
            missing_fields.append("Receiver Name")
        if not self.receiver_email:
            missing_fields.append("Receiver Email")

        if not self.reference_id:
            missing_fields.append("Mobile Reference")

        if missing_fields:
            raise ValidationError(
                f"The following required fields are missing or invalid: {', '.join(missing_fields)}"
            )

    def _check_skipcash_api_credentials(self):
        api_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.skipcash_api_url")
        )

        merchant_key = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.skipcash_merchant_key")
        )

        merchant_password = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("go_giftcard.skipcash_merchant_password")
        )

        missing_params = []
        if not api_url:
            missing_params.append("SkipCash API URL")
        if not merchant_key:
            missing_params.append("SkipCash Merchant Key")
        if not merchant_password:
            missing_params.append("SkipCash Merchant Password")

        if missing_params:
            raise ValidationError(
                f"Please configure the following SkipCash settings "
                f": {', '.join(missing_params)}"
            )

        return api_url, merchant_key, merchant_password
