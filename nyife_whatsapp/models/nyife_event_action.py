# -*- coding: utf-8 -*-
import json
import logging
import re
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# All available Odoo dynamic variables for CRM leads
LEAD_DYNAMIC_VARIABLES = [
    ('lead.name', 'Lead Name'),
    ('lead.contact_name', 'Contact Name'),
    ('lead.partner_name', 'Company Name'),
    ('lead.email_from', 'Email'),
    ('lead.phone', 'Phone'),
    ('lead.mobile', 'Mobile'),
    ('lead.street', 'Street'),
    ('lead.city', 'City'),
    ('lead.zip', 'Zip Code'),
    ('lead.country_id.name', 'Country'),
    ('lead.state_id.name', 'State'),
    ('lead.expected_revenue', 'Expected Revenue'),
    ('lead.probability', 'Probability (%)'),
    ('lead.stage_id.name', 'Stage Name'),
    ('lead.user_id.name', 'Salesperson'),
    ('lead.team_id.name', 'Sales Team'),
    ('lead.priority', 'Priority'),
    ('lead.source_id.name', 'Source'),
    ('lead.medium_id.name', 'Medium'),
    ('lead.campaign_id.name', 'Campaign'),
    ('lead.description', 'Internal Notes'),
    ('lead.date_deadline', 'Expected Closing'),
    ('lead.create_date', 'Creation Date'),
    ('lead.tag_ids.names', 'Tags'),
    ('lead.lost_reason_id.name', 'Lost Reason'),
]

# CRM event types
EVENT_TYPES = [
    ('lead_created', 'Lead Created'),
    ('lead_stage_changed', 'Stage Changed'),
    ('lead_won', 'Lead Won'),
    ('lead_lost', 'Lead Lost'),
    ('lead_assigned', 'Salesperson Assigned'),
    ('lead_probability_changed', 'Probability Changed'),
    ('lead_partner_changed', 'Customer Changed'),
    ('activity_created', 'Activity Created'),
    ('activity_due_today', 'Activity Due Today'),
    ('lead_updated', 'Lead Updated (Any Field)'),
]


class NyifeEventAction(models.Model):
    _name = 'nyife.event.action'
    _description = 'Nyife Event Action Mapping'
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    event_type = fields.Selection(
        selection=EVENT_TYPES,
        string='Event Type',
        required=True,
        index=True,
    )
    template_id = fields.Many2one(
        'nyife.template',
        string='WhatsApp Template',
        required=True,
        domain=[('status', '=', 'approved')],
        ondelete='restrict',
    )
    phone_field = fields.Selection([
        ('mobile', 'Mobile'),
        ('phone', 'Phone'),
    ], string='Send To', default='mobile', required=True,
        help='Which phone field on the lead to use for sending')

    variable_mapping_ids = fields.One2many(
        'nyife.variable.mapping', 'event_action_id',
        string='Variable Mappings',
    )

    stage_ids = fields.Many2many(
        'crm.stage',
        string='Specific Stages',
        help='Only trigger when lead enters these stages (leave empty for all stages). '
             'Applicable only for "Stage Changed" event.',
    )

    note = fields.Text(string='Notes')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Auto-populate variable mapping lines when template changes."""
        if self.template_id:
            variables = self.template_id.get_variables()
            mapping_vals = []
            for var in variables:
                mapping_vals.append((0, 0, {
                    'component_type': var.get('component_type', 'body'),
                    'variable_index': var.get('index', 1),
                    'odoo_field': '',
                    'static_value': '',
                }))
            self.variable_mapping_ids = [(5, 0, 0)] + mapping_vals

    def resolve_variable_value(self, lead, odoo_field, static_value):
        """Resolve a dynamic variable value from the lead record."""
        if static_value:
            return str(static_value)

        if not odoo_field:
            return ''

        # Remove 'lead.' prefix
        field_path = odoo_field.replace('lead.', '', 1) if odoo_field.startswith('lead.') else odoo_field

        record = lead
        parts = field_path.split('.')
        for part in parts:
            if part == 'names' and hasattr(record, 'mapped'):
                return ', '.join(record.mapped('name'))
            if hasattr(record, part):
                record = getattr(record, part)
                if record is False or record is None:
                    return ''
            else:
                return ''

        return str(record) if record else ''

    def send_whatsapp_for_lead(self, lead):
        """Send a WhatsApp template message for a given lead."""
        self.ensure_one()

        api_url = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.api_url', '')
        access_token = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.access_token', '')
        enabled = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.enabled', 'False')

        if enabled != 'True' or not api_url or not access_token:
            return False

        # Determine phone number
        phone = getattr(lead, self.phone_field, '') or ''
        if not phone:
            _logger.warning(
                'Nyife: No %s number for lead %s (ID: %s), skipping.',
                self.phone_field, lead.name, lead.id,
            )
            return False

        # Clean phone number
        phone = re.sub(r'[^\d+]', '', phone.strip())
        if not phone:
            return False

        # Build template components for API
        template = self.template_id
        components_data = template.get_components()

        # Group variable mappings by component type
        mappings_by_component = {}
        for mapping in self.variable_mapping_ids:
            comp_type = mapping.component_type.upper()
            if comp_type not in mappings_by_component:
                mappings_by_component[comp_type] = []
            value = self.resolve_variable_value(lead, mapping.odoo_field, mapping.static_value)
            mappings_by_component[comp_type].append({
                'index': mapping.variable_index,
                'value': value,
            })

        # Build request components
        request_components = []
        for comp_type, params_list in mappings_by_component.items():
            params_list.sort(key=lambda x: x['index'])
            parameters = []
            for param in params_list:
                parameters.append({
                    'type': 'text',
                    'text': param['value'],
                })
            request_components.append({
                'type': comp_type.lower(),
                'parameters': parameters,
            })

        # Build the API payload
        contact_name = lead.contact_name or lead.partner_name or lead.name or ''
        name_parts = contact_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        payload = {
            'phone': phone,
            'first_name': first_name,
            'last_name': last_name,
            'email': lead.email_from or '',
            'template': {
                'name': template.name,
                'language': template.language or 'en',
                'components': request_components,
            },
        }

        api_url = api_url.rstrip('/')
        url = f"{api_url}/api/send/template"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        log_vals = {
            'lead_id': lead.id,
            'event_action_id': self.id,
            'template_id': template.id,
            'phone': phone,
            'payload': json.dumps(payload, indent=2),
            'status': 'pending',
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response_data = response.json() if response.content else {}
            log_vals['response'] = json.dumps(response_data, indent=2)

            if response.status_code == 200 and response_data.get('data', {}).get('success', response_data.get('success', False)):
                log_vals['status'] = 'sent'
                messages = response_data.get('data', {}).get('data', {}).get('messages', [])
                if messages:
                    log_vals['message_id'] = messages[0].get('id', '')
            else:
                log_vals['status'] = 'failed'
                log_vals['error_message'] = response_data.get('message', f'HTTP {response.status_code}')

        except requests.exceptions.RequestException as e:
            log_vals['status'] = 'failed'
            log_vals['error_message'] = str(e)
            _logger.error('Nyife API error for lead %s: %s', lead.id, str(e))

        self.env['nyife.message.log'].sudo().create(log_vals)
        return log_vals.get('status') == 'sent'


class NyifeVariableMapping(models.Model):
    _name = 'nyife.variable.mapping'
    _description = 'Template Variable Mapping'
    _order = 'component_type, variable_index'

    event_action_id = fields.Many2one(
        'nyife.event.action',
        string='Event Action',
        required=True,
        ondelete='cascade',
    )
    component_type = fields.Selection([
        ('header', 'Header'),
        ('body', 'Body'),
        ('button', 'Button'),
    ], string='Component', required=True, default='body')

    variable_index = fields.Integer(
        string='Variable #',
        required=True,
        default=1,
        help='The placeholder index in the template (e.g., {{1}}, {{2}})',
    )
    odoo_field = fields.Selection(
        selection=LEAD_DYNAMIC_VARIABLES,
        string='Odoo Field',
        help='Select an Odoo CRM field to map to this template variable',
    )
    static_value = fields.Char(
        string='Static Value',
        help='Use a fixed value instead of an Odoo field (overrides Odoo Field if set)',
    )
