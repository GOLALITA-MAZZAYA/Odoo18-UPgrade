from odoo import models, fields
from .sms_request import SMSApi

SMS_STATUS = {
    "S": "Success",
    "1702": "Invalid URL. Missing or blank parameter.",
    "1703": "Invalid username or password.",
    "1704": "Invalid type parameter.",
    "1705": "Invalid message.",
    "1706": "Invalid destination.",
    "1707": "Invalid sender ID.",
    "1708": "Invalid value for DLR parameter.",
    "1709": "User validation failed.",
    "1710": "Internal error",
    "1725": "Insufficient credit.",
    "1715": "Response timeout.",
    "1032": "DND reject.",
    "1028": "Spam message.",
    "F": "Failed / IP not allowed."
}


class SMSMessage(models.Model):
    _name = "sms.message"
    _rec_name = "recipient"
    _description = "SMS Message"

    msg_config = fields.Many2one(
        "sms.config",
        string="SMS Configuration",
        required=True,
        help="Select the SMS configuration to be used for sending this message.",
    )
    recipient = fields.Char(
        string="Recipient Number",
        required=True,
        help="Enter the mobile number of the recipient (including country code).",
    )
    msg = fields.Text(
        string="Message Content",
        translate=True,
        required=True,
        help="Content of the SMS message to be sent.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("error", "Error"),
        ],
        string="State",
        default="draft",
        help="Current state of the SMS message.",
    )
    status_msg = fields.Char(
        string="Status Message",
        translate=True,
        help="Detailed status returned by the SMS gateway (e.g., success, failure reason).",
    )
    message_id = fields.Char(
        string="Gateway Message ID",
        help="Unique identifier for the message as returned by the SMS gateway.",
    )

    def action_state_draft(self):
        self.write({"state": "draft", "status_msg": False})

    def action_send_sms(self):
        for sms in self:
            sms.write({"state": "pending"})

            data = {
                "textmessage": sms.msg,
                "api_id": sms.msg_config.user_name,
                "api_password": sms.msg_config.password,
                "sms_type": "T",
                "encoding": "T",
                "phonenumber": sms.recipient,
                "sender_id": "GOLALITAAPP",
            }

            sms_api = SMSApi(sms.msg_config)
            response = sms_api.make_api_request(params=data)
            sms._process_sms_response(response)

    def _process_sms_response(self, response):
        sms = self

        if not response:
            sms.write({"state": "error", "status_msg": "No response from SMS API"})
            return

        code = response.get("status", "1710")
        message_id = response.get("message_id", "")

        status_msg = SMS_STATUS.get(code, f"Unknown response code")
        state = "sent" if code == "S" else "error"

        sms.write(
            {
                "message_id": message_id,
                "status_msg": status_msg,
                "state": state,
            }
        )
