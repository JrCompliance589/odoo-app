# -*- coding: utf-8 -*-
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    nyife_api_url = fields.Char(
        string='Nyife Instance URL',
        config_parameter='nyife_whatsapp.api_url',
        help='Your Nyife instance URL (e.g., https://your-domain.nyife.chat)',
    )
    nyife_access_token = fields.Char(
        string='API Access Token',
        config_parameter='nyife_whatsapp.access_token',
        help='API access token from your Nyife dashboard',
    )
    nyife_enabled = fields.Boolean(
        string='Enable WhatsApp Notifications',
        config_parameter='nyife_whatsapp.enabled',
        default=False,
    )

    def action_test_nyife_connection(self):
        """Test connectivity to Nyife API."""
        self.ensure_one()
        api_url = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.api_url', '')
        access_token = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.access_token', '')

        if not api_url or not access_token:
            raise UserError(_('Please configure Nyife URL and Access Token first and save.'))

        api_url = api_url.rstrip('/')
        url = f"{api_url}/api/verify"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Connection Successful'),
                        'message': _('Successfully connected to Nyife API!'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(
                    _('Connection failed. Status: %s. Please verify your URL and token.') % response.status_code
                )
        except requests.exceptions.ConnectionError:
            raise UserError(_('Could not connect to %s. Please verify the URL.') % api_url)
        except requests.exceptions.Timeout:
            raise UserError(_('Connection timed out. Please try again.'))

    def action_sync_nyife_templates(self):
        """Fetch templates from Nyife API and sync them locally."""
        self.ensure_one()
        api_url = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.api_url', '')
        access_token = self.env['ir.config_parameter'].sudo().get_param('nyife_whatsapp.access_token', '')

        if not api_url or not access_token:
            raise UserError(_('Please configure Nyife URL and Access Token first.'))

        api_url = api_url.rstrip('/')
        url = f"{api_url}/api/templates"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }

        all_templates = []
        page = 1

        try:
            while True:
                response = requests.get(url, headers=headers, params={'page': page, 'per_page': 100}, timeout=30)
                if response.status_code != 200:
                    raise UserError(_('Failed to fetch templates. Status: %s') % response.status_code)

                data = response.json()
                templates = data.get('data', [])
                if not templates:
                    break

                all_templates.extend(templates)

                # Check if there are more pages
                last_page = data.get('meta', {}).get('last_page', data.get('last_page', 1))
                if page >= last_page:
                    break
                page += 1

        except requests.exceptions.RequestException as e:
            raise UserError(_('Error fetching templates: %s') % str(e))

        template_model = self.env['nyife.template']
        synced = 0

        for tmpl in all_templates:
            nyife_id = str(tmpl.get('id', ''))
            name = tmpl.get('name', '')
            metadata = tmpl.get('metadata', {})
            components = metadata.get('components', []) if isinstance(metadata, dict) else []
            uuid = tmpl.get('uuid', '')
            language = tmpl.get('language', 'en')
            status = tmpl.get('status', 'APPROVED')

            # Extract variables from components
            variables = []
            body_text = ''
            header_text = ''
            for comp in components:
                comp_type = comp.get('type', '').upper()
                text = comp.get('text', '')
                if comp_type == 'BODY':
                    body_text = text
                elif comp_type == 'HEADER' and comp.get('format', '').upper() == 'TEXT':
                    header_text = text

                # Find {{n}} placeholders
                import re
                placeholders = re.findall(r'\{\{(\d+)\}\}', text)
                for p in placeholders:
                    var_key = f"{comp_type.lower()}_{p}"
                    if var_key not in [v['key'] for v in variables]:
                        variables.append({
                            'key': var_key,
                            'component_type': comp_type.lower(),
                            'index': int(p),
                            'sample': '',
                        })

            existing = template_model.search([('nyife_id', '=', nyife_id)], limit=1)
            vals = {
                'name': name,
                'nyife_id': nyife_id,
                'nyife_uuid': uuid,
                'language': language,
                'status': status.lower(),
                'body_text': body_text,
                'header_text': header_text,
                'components_json': json.dumps(components),
                'variables_json': json.dumps(variables),
            }

            if existing:
                existing.write(vals)
            else:
                template_model.create(vals)
            synced += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Templates Synced'),
                'message': _('%d templates synced from Nyife.') % synced,
                'type': 'success',
                'sticky': False,
            }
        }
