import os
import json
import urllib.request
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-emails', methods=['POST'])
@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    api_key = os.environ.get('RESEND_API_KEY')

    if not api_key:
        return jsonify({'success': False, 'error': 'RESEND_API_KEY missing in Render Environment.'}), 500

    data = request.json or {}
    contacts = data.get('contacts', [])
    subject = data.get('subject', 'Notification')
    template = data.get('template', '')

    sent_count = 0
    error_msg = None

    for contact in contacts:
        name = contact.get('Name') or contact.get('name') or ''
        email = contact.get('Email') or contact.get('email') or ''

        if not email:
            continue

        content = template.replace('[Name]', name)

        payload = json.dumps({
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": subject,
            "html": f"<p>{content}</p>"
        }).encode('utf-8')

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 201):
                    sent_count += 1
        except Exception as e:
            error_msg = str(e)

    if sent_count > 0:
        return jsonify({'success': True, 'count': sent_count})
    else:
        return jsonify({'success': False, 'error': error_msg or 'Failed to send email via API.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
