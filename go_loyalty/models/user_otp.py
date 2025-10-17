# -*- coding: utf-8 -*-
import logging
import random

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

OTP_EXPIRE_MIN = 5


def generateOTP(length=4):

    digits = list(range(10))
    otp = []

    while len(otp) < length:
        candidate = random.choice(digits)

        if otp and abs(candidate - otp[-1]) == 1:
            continue

        otp.append(candidate)
        digits.remove(candidate)

    return "".join(map(str, otp))


class AuthOTP(models.Model):
    _name = "user.otp"
    _description = "One-Time Password"
    _order = "create_date desc, id desc"
    _rec_name = "otp_code"

    @api.model
    def _get_default_otp(self):
        return generateOTP()

    @api.model
    def _get_default_expired_date(self):
        return fields.Datetime.now() + relativedelta(minutes=OTP_EXPIRE_MIN)

    otp_code = fields.Char(
        default=_get_default_otp,
        string="OTP",
        required=True,
        index=True,
        copy=False,
    )
    phone = fields.Char(string="Phone", index=True)
    otp_login = fields.Char(
        string="Login Key",
        required=True,
        index=True,
        copy=False,
    )
    is_used = fields.Boolean(default=False, index=True)
    otp_type = fields.Selection(
        [
            ("login", "Login"),
            ("signup", "Signup"),
            ("reset", "Reset Password"),
            ("other", "Other"),
        ],
        required=True,
        index=True,
    )

    otp_expire_date = fields.Datetime(
        default=_get_default_expired_date,
        string="Expires At",
        required=True,
        index=True,
    )

    @api.model
    def _now(self):
        return fields.Datetime.now()

    @api.autovacuum
    def _vacuum_expired_otp(self):
        """Periodic cleanup for expired or stale OTPs."""
        # Expired
        expired = self.search([("otp_expire_date", "<", self._now())])
        if expired:
            _logger.info("OTP GC: removing %s expired OTP(s)", len(expired))
            expired.unlink()

    @api.model
    def is_valid_otp(self, login, otp, otp_type="reset"):
        """Verify OTP and mark it as used."""
        user_otp = self.search(
            [
                ("otp_code", "=", otp),
                ("otp_login", "=", login),
                ("otp_type", "=", otp_type),
                ("is_used", "=", False),
                ("otp_expire_date", ">", fields.Datetime.now()),
            ],
            limit=1,
        )
        if user_otp:
            user_otp.is_used = True
        return bool(user_otp)

    @api.model
    def generate_and_send_otp(self, login, phone, otp_type="reset"):
        """Generate OTP and send via SMS."""
        # Remove previous OTPs for this user & type
        self.search([("otp_login", "=", login), ("otp_type", "=", otp_type)]).unlink()

        otp = self.create(
            {
                "otp_login": login,
                "phone": phone,
                "otp_type": otp_type,
            }
        )
        _logger.info("Generated OTP: %s for %s", otp.otp_code, login)
        try:
            return otp._send_otp(phone)
        except Exception as e:
            _logger.error("Failed to send OTP via SMS: %s", e)
            return False

    @api.model
    def generate_and_send_otp_email(self, login, email, otp_type="reset"):
        """Generate OTP and send via email."""
        self.search([("otp_login", "=", login), ("otp_type", "=", otp_type)]).unlink()

        otp = self.create(
            {
                "otp_login": login,
                "phone": "N/A",
                "otp_type": otp_type,
            }
        )
        _logger.info("Generated OTP (Email): %s for %s", otp.otp_code, login)
        try:
            return otp._send_otp_email(email)
        except Exception as e:
            _logger.error("Failed to send OTP via Email: %s", e)
            return False

    @api.model
    def _send_otp_email(self, email):
        """Send OTP via email."""
        body = f"""
            <p>Dear Customer,</p>
            
            <p>Kindly use <strong>{self.otp_code}</strong> for your one-time password, as requested.<br>
            Please ignore if you did not generate this OTP.</p>
            
            <hr>
            
            <p>ارجو إدخال رمز التحقق <strong>{self.otp_code}</strong> كلمة السر لمرة واحدة فقط لإتمام عملية التسجيل.<br>
            يرجى تجاهل هذه الرسالة إذا لم تطلب رمز التحقق.</p>
        """
        self.env["mail.mail"].create(
            {
                "subject": "Password Reset - OTP Verification",
                "body_html": body,
                "email_from": "no_reply@golalita.com",
                "email_to": email,
                "auto_delete": True,
            }
        ).send()
        return True

    @api.model
    def _send_otp(self, phone):
        """Send OTP via SMS."""
        message_provider = self.env["sms.config"].sudo().search([], limit=1)
        if not message_provider:
            _logger.warning("No SMS provider configured.")
            return False

        sms_values = {
            "msg_config": message_provider.id,
            "recipient": phone,
            "msg": f"""
                Dear Golalita Customer, 
                Kindly use {self.otp_code} for your one-time password, as requested.
                Please ignore if OTP not generated by you!
            """,
        }
        sms = self.env["sms.message"].create(sms_values)
        sms.action_send_sms()
        return sms.state == "sent"
