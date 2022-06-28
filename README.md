# What is it?

You're terrible at replying to people. Get email reminders to do so.

# Usage

1. Install requirements: `pip install -r requirements.txt`
2. Go to [Google security settings](https://myaccount.google.com/security), generate an 'App password' for Mail.
3. Create a `.env` file with your info:

```bash
EMAIL:'<your_email>'
PASSWORD:'<16_string_password_from_step_2>'
```

4. Run: `python whatsapp_reminder.py`

The first time you run the script, you will need to scan the QR code via your phone. After that, it should be automatic.

5. Run `./cronjob` to add a new cron task to run daily at 2pm.
