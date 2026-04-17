# -*- coding: utf-8 -*-
from odoo import fields, models


class NyifeMessageLog(models.Model):
    _name = 'nyife.message.log'
    _description = 'Nyife WhatsApp Message Log'
    _order = 'create_date desc'
    _rec_name = 'phone'

    lead_id = fields.Many2one('crm.lead', string='Lead', index=True, ondelete='set null')
    event_action_id = fields.Many2one('nyife.event.action', string='Event Action', ondelete='set null')
    template_id = fields.Many2one('nyife.template', string='Template', ondelete='set null')
    phone = fields.Char(string='Phone Number')
    payload = fields.Text(string='Request Payload')
    response = fields.Text(string='API Response')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], string='Status', default='pending', index=True)
    error_message = fields.Text(string='Error')
    message_id = fields.Char(string='WhatsApp Message ID')
