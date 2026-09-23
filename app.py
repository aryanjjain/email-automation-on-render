import os
import socket
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify

# Force Python socket to resolve IPv4 addresses only
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [res for res in responses if res[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send-emails', methods=['POST'])
@app.route('/api/send-emails', methods=['POST'])
def send_emails():
    sender_email = os.environ.get('SENDER_EMAIL')
    app_password = os.environ.get('APP_PASSWORD')

    if not sender_email or not app_password:
        return jsonify({'success': False, 'error': 'Server credentials missing.'}), 500

    data = request.json or {}
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
    app.run(host='0.0.0.0', port=5000)
