# Publishing Nyife WhatsApp Module to Odoo App Store

## Step-by-Step Guide

### 1. Create an Odoo Publisher Account

1. Go to **https://www.odoo.com/my/home**
2. Sign in or create a new Odoo account
3. Navigate to **https://apps.odoo.com/apps/dashboard**
4. Click **"Become a Publisher"** and fill in your publisher profile:
   - Publisher Name: **Nyife**
   - Website: **https://nyife.chat**
   - Support Email: **support@nyife.chat**
   - Logo / Icon

### 2. Prepare the Module for Submission

#### Required Files Checklist:
- [x] `__manifest__.py` — with proper metadata (name, version, category, license, etc.)
- [x] `__init__.py` — module entry point
- [x] `static/description/index.html` — Odoo app store listing page (HTML)
- [ ] `static/description/icon.png` — 128×128 PNG module icon (YOU NEED TO CREATE THIS)
- [ ] `static/description/banner.png` — 750×240 banner image (YOU NEED TO CREATE THIS)
- [ ] Screenshots — at least 3-5 screenshots in `static/description/` showing the module in action

#### Create the Icon & Banner:
- **icon.png**: 128×128px PNG with the Nyife/WhatsApp branding
- **banner.png**: 750×240px PNG with module name and key features

#### Create Screenshots:
Install the module on a test Odoo instance and take screenshots of:
1. Settings page (API URL + token configuration)
2. Template list view (synced templates)
3. Event Action form (event type + template mapping + variable mapping)
4. CRM Lead form with WhatsApp stat button
5. Message log list view

Save screenshots as:
- `static/description/screenshot_01_settings.png`
- `static/description/screenshot_02_templates.png`
- `static/description/screenshot_03_event_action.png`
- `static/description/screenshot_04_lead_form.png`
- `static/description/screenshot_05_message_logs.png`

### 3. Test the Module

Before submitting, thoroughly test on a clean Odoo 17.0 instance:

```bash
# Install on your Odoo instance
cp -r nyife_whatsapp /path/to/odoo/addons/
# Restart Odoo
sudo systemctl restart odoo
# Update apps list, then install from Apps menu
```

Test checklist:
- [ ] Module installs without errors
- [ ] Settings page shows Nyife configuration
- [ ] Test Connection button works with valid credentials
- [ ] Sync Templates fetches templates correctly
- [ ] Event actions can be created with variable mappings
- [ ] Creating a lead triggers the "Lead Created" event and sends a WhatsApp
- [ ] Changing a lead stage triggers the "Stage Changed" event
- [ ] Manual send wizard works from the lead form
- [ ] Message logs show correct statuses
- [ ] Uninstall and reinstall works cleanly

### 4. Package the Module

```bash
# Create a zip file for upload
cd /path/to/odoo-nyife-whatsapp/
zip -r nyife_whatsapp.zip nyife_whatsapp/ \
    -x "nyife_whatsapp/__pycache__/*" \
    -x "nyife_whatsapp/**/__pycache__/*" \
    -x "nyife_whatsapp/.git/*"
```

### 5. Submit to Odoo App Store

1. Go to **https://apps.odoo.com/apps/dashboard**
2. Click **"Submit a Module"**
3. Fill in the form:
   - **Module ZIP**: Upload `nyife_whatsapp.zip`
   - **Odoo Version**: 17.0
   - **Category**: Marketing / WhatsApp
   - **License**: LGPL-3
   - **Price**: Free (or set a price)
   - **Summary**: "Send WhatsApp notifications on CRM lead events via Nyife"
4. Upload the **icon**, **banner**, and **screenshots**
5. Submit for **review**

### 6. Odoo Review Process

Odoo will review your module for:
- **Code quality** — follows OCA/Odoo coding standards
- **Security** — no SQL injection, XSS, or unsafe code
- **Functionality** — module works as described
- **Description quality** — clear listing page with screenshots
- **License compliance** — LGPL-3 is standard

Review typically takes **5-15 business days**. You may receive feedback requesting changes.

### 7. After Approval

Once approved:
- Your module appears on **https://apps.odoo.com**
- Users can install it directly from the Odoo Apps menu
- You can push version updates through the dashboard

---

## Versioning Convention

Use the format: `{odoo_version}.{major}.{minor}.{patch}`

- Current: `17.0.1.0.0`
- Bug fix: `17.0.1.0.1`
- New feature: `17.0.1.1.0`
- Breaking change: `17.0.2.0.0`

## Supporting Multiple Odoo Versions

To support Odoo 16.0, 15.0, etc., create separate branches or copies with:
- Updated `__manifest__.py` version (e.g., `16.0.1.0.0`)
- API compatibility adjustments (e.g., `attrs` vs `invisible` attribute syntax)
- Each version is submitted as a separate module on the app store

## Odoo Online (SaaS) Note

Odoo Online does not allow custom modules or modules from the Odoo Apps Store,
so this module will remain unavailable for Odoo Online in the listing.

Optional fallback for no-addon automation is available via Nyife API bridge:

- `GET /api/odoo-online/templates`
- `POST /api/odoo-online/send-template`

## Pricing Options

- **Free**: Great for adoption. Users get the module for free, you monetize through Nyife subscriptions.
- **One-time purchase**: Set a price per version (e.g., $49, $99).
- **Subscription**: Not directly supported by Odoo store — use the SaaS/service model through Nyife instead.

**Recommended**: Keep the Odoo module **free** to maximize installations. Revenue comes from Nyife platform subscriptions (API usage, template sending, WhatsApp Business API fees).
