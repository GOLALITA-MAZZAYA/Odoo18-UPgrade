from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _get_whatsapp_connection(self):
        params = self.env['ir.config_parameter'].sudo()
        api_url = params.get_param('go_whatsapp.whatsapp_api_url')
        api_token = params.get_param('go_whatsapp.whatsapp_api_token')
        instance_id = params.get_param('go_whatsapp.whatsapp_instance_id')

        missing_params = []
        if not api_url:
            missing_params.append('WhatsApp API URL')
        if not api_token:
            missing_params.append('WhatsApp API Token')
        if not instance_id:
            missing_params.append('WhatsApp Instance ID')

        if missing_params:
            raise UserError(_("Missing WhatsApp configuration parameters: %s") % ', '.join(missing_params))

        return WhatsAppConnection(api_url, api_token, instance_id)

    @api.model
    def _send_sms(self, numbers, message):
        connection = self._get_whatsapp_connection()
        params = {'numbers': numbers, 'message': message}
        return connection._connect_with_whatsapp_api(params)

    @api.model
    def _send_sms_batch(self, messages):
        connection = self._get_whatsapp_connection()
        result = []
        for msg in messages:
            res = connection._connect_with_whatsapp_api({
                'numbers': msg['number'],
                'message': msg['content'],
            })
            result.append({
                'res_id': msg['res_id'],
                'state': res.get('state', 'error'),
                'message': res.get('message', ''),
            })
        return result