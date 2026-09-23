import os
import smtplib
from email.message import EmailMessage
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    # Safely retrieve credentials from cloud environment variables
    sender_email = os.environ.get('SENDER_EMAIL')
    app_password = os.environ.get('APP_PASSWORD')

    if not sender_email or not app_password:
        return jsonify({'success': False, 'error': 'Server credentials not configured'}), 500

    data = request.json
    contacts = data.get('contacts', [])
    subject = data.get('subject', 'Notification')
    template = data.get('template', '')

    try:
       server = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        server.starttls()
        server.login(sender_email, app_password)

        sent_count = 0
        for contact in contacts:
            name = contact.get('Name') or contact.get('name') or ''
            email = contact.get('Email') or contact.get('email') or ''

            if not email:
                continue

            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = email
            msg.set_content(template.replace('[Name]', name))

            server.send_message(msg)
            sent_count += 1

        server.quit()
        return jsonify({'success': True, 'count': sent_count})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
