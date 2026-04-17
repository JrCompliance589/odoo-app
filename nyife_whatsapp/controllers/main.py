# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class NyifeWebhookController(http.Controller):

    @http.route('/nyife/webhook/status', type='json', auth='public', methods=['POST'], csrf=False)
    def webhook_message_status(self, **kwargs):
        """Receive message delivery status updates from Nyife."""
        data = request.jsonrequest
        message_id = data.get('message_id', '')
        status = data.get('status', '')

        if message_id and status:
            log = request.env['nyife.message.log'].sudo().search(
                [('message_id', '=', message_id)], limit=1
            )
            if log:
                log.write({'status': status if status in ('sent', 'failed') else log.status})

        return {'status': 'ok'}
