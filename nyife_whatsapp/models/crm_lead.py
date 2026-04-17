# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    nyife_message_log_ids = fields.One2many(
        'nyife.message.log', 'lead_id', string='WhatsApp Messages',
    )
    nyife_message_count = fields.Integer(
        string='WhatsApp Messages',
        compute='_compute_nyife_message_count',
    )

    def _compute_nyife_message_count(self):
        log_data = self.env['nyife.message.log'].sudo().read_group(
            [('lead_id', 'in', self.ids)],
            ['lead_id'],
            ['lead_id'],
        )
        mapped = {d['lead_id'][0]: d['lead_id_count'] for d in log_data}
        for lead in self:
            lead.nyife_message_count = mapped.get(lead.id, 0)

    def _trigger_nyife_event(self, event_type, old_values=None):
        """Find matching event actions and send WhatsApp messages."""
        event_actions = self.env['nyife.event.action'].sudo().search([
            ('event_type', '=', event_type),
            ('active', '=', True),
        ])

        for lead in self:
            for action in event_actions:
                # Stage filter: only apply for stage_changed events
                if event_type == 'lead_stage_changed' and action.stage_ids:
                    if lead.stage_id not in action.stage_ids:
                        continue

                try:
                    action.send_whatsapp_for_lead(lead)
                except Exception as e:
                    _logger.error(
                        'Nyife: Error sending WhatsApp for lead %s event %s: %s',
                        lead.id, event_type, str(e),
                    )

    @api.model_create_multi
    def create(self, vals_list):
        """Trigger WhatsApp on lead creation."""
        leads = super().create(vals_list)
        leads._trigger_nyife_event('lead_created')
        return leads

    def write(self, vals):
        """Trigger WhatsApp on lead updates based on changed fields."""
        # Capture old values before write
        old_stages = {lead.id: lead.stage_id.id for lead in self} if 'stage_id' in vals else {}
        old_users = {lead.id: lead.user_id.id for lead in self} if 'user_id' in vals else {}
        old_probabilities = {lead.id: lead.probability for lead in self} if 'probability' in vals else {}
        old_partners = {lead.id: lead.partner_id.id for lead in self} if 'partner_id' in vals else {}

        result = super().write(vals)

        # Stage changed
        if 'stage_id' in vals:
            changed_leads = self.filtered(lambda l: old_stages.get(l.id) != l.stage_id.id)
            if changed_leads:
                changed_leads._trigger_nyife_event('lead_stage_changed')

                # Check for Won stage
                won_leads = changed_leads.filtered(lambda l: l.stage_id.is_won)
                if won_leads:
                    won_leads._trigger_nyife_event('lead_won')

        # Lead lost (active set to False with lost_reason or via action_set_lost)
        if vals.get('active') is False or 'lost_reason_id' in vals:
            self._trigger_nyife_event('lead_lost')

        # Salesperson assigned/changed
        if 'user_id' in vals:
            changed_leads = self.filtered(lambda l: old_users.get(l.id) != l.user_id.id)
            if changed_leads:
                changed_leads._trigger_nyife_event('lead_assigned')

        # Probability changed
        if 'probability' in vals:
            changed_leads = self.filtered(lambda l: old_probabilities.get(l.id) != l.probability)
            if changed_leads:
                changed_leads._trigger_nyife_event('lead_probability_changed')

        # Customer/partner changed
        if 'partner_id' in vals:
            changed_leads = self.filtered(lambda l: old_partners.get(l.id) != l.partner_id.id)
            if changed_leads:
                changed_leads._trigger_nyife_event('lead_partner_changed')

        # General update event
        if vals:
            self._trigger_nyife_event('lead_updated')

        return result

    def action_view_nyife_messages(self):
        """Open the message log for this lead."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'WhatsApp Messages',
            'res_model': 'nyife.message.log',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id},
        }


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.model_create_multi
    def create(self, vals_list):
        """Trigger WhatsApp when an activity is created on a lead."""
        activities = super().create(vals_list)
        for activity in activities:
            if activity.res_model == 'crm.lead' and activity.res_id:
                lead = self.env['crm.lead'].browse(activity.res_id)
                if lead.exists():
                    lead._trigger_nyife_event('activity_created')
        return activities
