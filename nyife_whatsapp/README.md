# Nyife WhatsApp Notifications for Odoo CRM

Automatically send WhatsApp template messages on CRM lead events via the Nyife WhatsApp Business API.

## Features

- **10 CRM Event Types**: Lead created, stage changed, won, lost, salesperson assigned, probability changed, customer changed, activity created, activity due today, and general updates.
- **Template Sync**: One-click sync of all approved WhatsApp templates from your Nyife account.
- **Dynamic Variable Mapping**: Map template placeholders (`{{1}}`, `{{2}}`, ...) to 20+ Odoo CRM fields or static values.
- **Automatic Triggers**: Configure event-to-template mappings. Messages send automatically on events.
- **Manual Send**: Send WhatsApp directly from any lead form.
- **Full Logging**: Request/response payloads, delivery status, error tracking per message.
- **Stage Filters**: For stage-change events, restrict triggering to specific pipeline stages.
- **Daily Cron**: Scheduled action sends reminders for activities due today.

## Installation

1. Copy the `nyife_whatsapp` folder into your Odoo addons directory.
2. Restart the Odoo server.
3. Go to **Apps** → Update Apps List → Search for "Nyife WhatsApp" → Install.

## Configuration

1. Go to **Settings → Nyife WhatsApp**.
2. Enter your **Nyife Instance URL** (e.g., `https://your-domain.nyife.chat`).
3. Enter your **API Access Token** from the Nyife dashboard.
4. Click **Test Connection** to verify.
5. Click **Sync Templates** to import your approved WhatsApp templates.
6. Go to **Nyife WhatsApp → Configuration → Event Actions** and create your automation rules.

## Requirements

- Odoo 17.0 (Community or Enterprise)
- CRM module installed
- Nyife account with WhatsApp Business API
- API access token
- Approved WhatsApp message templates

## License

LGPL-3

## Support

- Email: support@nyife.chat
- Website: https://nyife.chat
