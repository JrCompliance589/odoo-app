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

## Odoo Online Support

As per Odoo's official policy, Odoo Online does not allow custom modules or modules
from the Odoo Apps Store. Because of that platform restriction, this addon will show
as unavailable for Odoo Online.

Optional fallback (works without module automation) via Nyife bridge API endpoints from
Odoo automated actions/webhooks:

- `GET /api/odoo-online/templates`
- `POST /api/odoo-online/send-template`

Both endpoints require `Authorization: Bearer <nyife_api_token>`.

### Example: Send Template From Odoo Online

Use Odoo Automation/Webhook to send JSON similar to:

```json
{
  "phone": "{{record.mobile or record.phone}}",
  "first_name": "{{record.contact_name}}",
  "email": "{{record.email_from}}",
  "template_name": "lead_created",
  "language": "en",
  "variables": {
    "1": "{{record.name}}",
    "2": "{{record.stage_id.name}}"
  }
}
```

Notes:

- `variables` maps to body placeholders (`{{1}}`, `{{2}}`, ...).
- Optional `header_variables` can be sent for header placeholders.
- The bridge endpoint forwards to Nyife's existing send-template flow so billing,
  template checks, subscription checks, and WhatsApp connection validation remain enforced.

## License

LGPL-3

## Support

- Email: [support@nyife.chat](mailto:support@nyife.chat)
- Website: [https://nyife.chat](https://nyife.chat)
