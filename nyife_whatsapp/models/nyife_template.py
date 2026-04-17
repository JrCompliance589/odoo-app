# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _


class NyifeTemplate(models.Model):
    _name = 'nyife.template'
    _description = 'Nyife WhatsApp Template'
    _order = 'name'

    name = fields.Char(string='Template Name', required=True, index=True)
    nyife_id = fields.Char(string='Nyife Template ID', index=True)
    nyife_uuid = fields.Char(string='Nyife UUID')
    language = fields.Char(string='Language', default='en')
    status = fields.Selection([
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
    ], string='Status', default='approved')
    body_text = fields.Text(string='Body Text')
    header_text = fields.Char(string='Header Text')
    components_json = fields.Text(string='Components (JSON)')
    variables_json = fields.Text(string='Variables (JSON)')
    event_action_ids = fields.One2many(
        'nyife.event.action', 'template_id', string='Event Actions',
    )

    def get_variables(self):
        """Parse and return variables list from JSON."""
        self.ensure_one()
        if self.variables_json:
            try:
                return json.loads(self.variables_json)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    def get_components(self):
        """Parse and return components from JSON."""
        self.ensure_one()
        if self.components_json:
            try:
                return json.loads(self.components_json)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
