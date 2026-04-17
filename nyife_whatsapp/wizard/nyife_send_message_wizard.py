# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class NyifeSendMessageWizard(models.TransientModel):
    _name = 'nyife.send.message.wizard'
    _description = 'Send WhatsApp Message Wizard'

    lead_id = fields.Many2one('crm.lead', string='Lead', required=True)
    template_id = fields.Many2one(
        'nyife.template',
        string='Template',
        required=True,
        domain=[('status', '=', 'approved')],
    )
    phone_field = fields.Selection([
        ('mobile', 'Mobile'),
        ('phone', 'Phone'),
    ], string='Send To', default='mobile', required=True)

    phone_preview = fields.Char(string='Phone Number', compute='_compute_phone_preview')
    body_preview = fields.Text(string='Template Body', related='template_id.body_text', readonly=True)

    variable_line_ids = fields.One2many(
        'nyife.send.message.wizard.line', 'wizard_id', string='Variables',
    )

    @api.depends('lead_id', 'phone_field')
    def _compute_phone_preview(self):
        for wiz in self:
            if wiz.lead_id and wiz.phone_field:
                wiz.phone_preview = getattr(wiz.lead_id, wiz.phone_field, '') or ''
            else:
                wiz.phone_preview = ''

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Populate variable lines from template."""
        if self.template_id:
            variables = self.template_id.get_variables()
            lines = []
            for var in variables:
                lines.append((0, 0, {
                    'component_type': var.get('component_type', 'body'),
                    'variable_index': var.get('index', 1),
                    'value': '',
                }))
            self.variable_line_ids = [(5, 0, 0)] + lines

    def action_send(self):
        """Send the WhatsApp message now."""
        self.ensure_one()

        if not self.phone_preview:
            raise UserError(_('The selected phone field is empty on this lead.'))

        # Build a temporary event action to reuse the sending logic
        mappings_by_component = {}
        for line in self.variable_line_ids:
            comp_type = line.component_type.upper()
            if comp_type not in mappings_by_component:
                mappings_by_component[comp_type] = []
            mappings_by_component[comp_type].append({
                'index': line.variable_index,
                'value': line.value or '',
            })

        # Create a temporary event action
        temp_action = self.env['nyife.event.action'].sudo().create({
            'name': f'Manual send - {self.lead_id.name}',
            'event_type': 'lead_updated',
            'template_id': self.template_id.id,
            'phone_field': self.phone_field,
            'active': False,  # Don't trigger on events
        })

        # Create variable mappings
        for line in self.variable_line_ids:
            self.env['nyife.variable.mapping'].sudo().create({
                'event_action_id': temp_action.id,
                'component_type': line.component_type,
                'variable_index': line.variable_index,
                'static_value': line.value or '',
            })

        success = temp_action.send_whatsapp_for_lead(self.lead_id)

        # Clean up temporary action
        temp_action.sudo().unlink()

        if success:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Message Sent'),
                    'message': _('WhatsApp message sent successfully!'),
                    'type': 'success',
                    'sticky': False,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Send Failed'),
                    'message': _('Failed to send WhatsApp message. Check the message logs for details.'),
                    'type': 'warning',
                    'sticky': True,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }


class NyifeSendMessageWizardLine(models.TransientModel):
    _name = 'nyife.send.message.wizard.line'
    _description = 'Send Message Wizard Variable Line'

    wizard_id = fields.Many2one('nyife.send.message.wizard', string='Wizard', ondelete='cascade')
    component_type = fields.Selection([
        ('header', 'Header'),
        ('body', 'Body'),
        ('button', 'Button'),
    ], string='Component', default='body')
    variable_index = fields.Integer(string='Variable #', default=1)
    value = fields.Char(string='Value')
