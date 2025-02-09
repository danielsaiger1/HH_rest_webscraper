from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

today = datetime.today().strftime('%Y%m%d')
    
file_path = f'./api/data/{today}_data_transformed.json'

with open(file_path, 'r') as file:
    data = json.load(file)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', restaurants=data)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# Route, um das Formular zu verarbeiten und E-Mail zu senden
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    # E-Mail senden
    send_email(name, email, message)
    
    return redirect('/contact')

# Funktion, um die E-Mail zu senden
def send_email(name, email, message):
    sender_email = os.getenv('GMAIL_MAIL_ADRESS')  # Deine Gmail-Adresse
    receiver_email = os.getenv('GMAIL_MAIL_ADRESS')  # Deine Ziel-E-Mail-Adresse (kann die gleiche sein)
    
    # Hole das App-Passwort aus den Umgebungsvariablen
    password = os.getenv('GMAIL_APP_PASSWORD') 
    
    # E-Mail-Nachricht erstellen
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Message from {name}"

    body = f"You recieved a new message from {name} ({email}):\n\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    # E-Mail versenden
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # TLS-Verschlüsselung aktivieren
            server.login(sender_email, password)  # Login mit deinem Gmail-Account und App-Passwort
            server.sendmail(sender_email, receiver_email, msg.as_string())  # E-Mail senden
    except Exception as e:
        print(f"Error while sending the mail: {e}")

if __name__ == '__main__':
    app.run(debug=True)