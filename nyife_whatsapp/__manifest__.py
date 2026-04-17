# -*- coding: utf-8 -*-
{
    'name': 'Nyife WhatsApp Notifications',
    'version': '17.0.1.0.0',
    'category': 'Marketing/WhatsApp',
    'summary': 'Send WhatsApp notifications on CRM lead events via Nyife',
    'description': """
Nyife WhatsApp Notifications for Odoo CRM
==========================================

Automatically send WhatsApp template messages to leads on various CRM events:

* Lead Created
* Lead Stage Changed
* Lead Won / Lost
* Lead Assigned to Salesperson
* Activity Due / Created
* Lead Updated (custom field triggers)

**Features:**
- Connect your Nyife account via API access token
- Fetch and sync approved WhatsApp templates from Nyife
- Map Odoo dynamic variables (lead name, phone, email, stage, etc.) to template placeholders
- Configure which template to send on each event type
- Message delivery logs and status tracking
- Manual send option from lead form view

**Requirements:**
- A Nyife account with WhatsApp Business API configured
- API access token from your Nyife dashboard
- Approved WhatsApp message templates
    """,
    'author': 'Nyife',
    'website': 'https://nyife.chat',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/nyife_event_data.xml',
        'views/res_config_settings_views.xml',
        'views/nyife_template_views.xml',
        'views/nyife_event_action_views.xml',
        'views/nyife_message_log_views.xml',
        'views/crm_lead_views.xml',
        'views/menu_views.xml',
        'wizard/nyife_send_message_wizard_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0,
    'currency': 'USD',
}
