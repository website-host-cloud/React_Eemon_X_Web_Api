from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS so your React frontend can talk to Flask
CORS(app)

# --- Twilio Credentials ---
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886' 
COMPANY_WHATSAPP_TO = 'whatsapp:+919486802976'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- Email Credentials ---
SENDER_EMAIL = os.getenv('SENDER_EMAIL')      
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') 

# --- Updated Root Route (Health Check) ---
@app.route('/')
def home():
    # Returns a simple JSON response for Render's health checks instead of looking for HTML
    return jsonify({
        "status": "online", 
        "service": "Eemon X Backend API",
        "message": "System operational."
    }), 200

@app.route('/send-whatsapp', methods=['POST'])
def process_form():
    data = request.json
    
    # Extract data from the frontend
    name = data.get('name', 'N/A')
    phone = data.get('phone', 'N/A')
    user_email = data.get('email', 'N/A')
    service = data.get('service', 'N/A')
    user_message = data.get('message', 'N/A')

    # ---------------------------------------------------------
    # 1. SEND WHATSAPP TO EEMON X TEAM
    # ---------------------------------------------------------
    whatsapp_body = f"""🚀 *New Lead for Eemon X!*

👤 *Name:* {name}
📞 *Phone:* {phone}
📧 *Email:* {user_email}
💼 *Service:* {service}

📝 *Message:*
{user_message}"""

    try:
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=whatsapp_body,
            to=COMPANY_WHATSAPP_TO
        )
        print(f"WhatsApp sent SID: {msg.sid}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return jsonify({"status": "error", "message": "Failed to send WhatsApp alert."}), 500

    # ---------------------------------------------------------
    # 2. SEND AUTO-REPLY EMAIL TO THE USER
    # ---------------------------------------------------------
    email_subject = f"Thank you for contacting Eemon X, {name}!"
    
    email_body = f"""Hi {name},

Thank you for reaching out to Eemon X. We have received your inquiry regarding {service}.

Here is a copy of the details you submitted:
-------------------------------------------------
Name: {name}
Phone: {phone}
Email: {user_email}
Service Required: {service}

Your Message:
{user_message}
-------------------------------------------------

Our team will review your requirements and a specialist will get back to you shortly.

Best regards,
The Eemon X Team
Official Comm: eemonx2025@gmail.com
"""

    try:
        email_msg = MIMEMultipart()
        email_msg['From'] = SENDER_EMAIL
        email_msg['To'] = user_email
        email_msg['Subject'] = email_subject
        email_msg.attach(MIMEText(email_body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() 
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(email_msg)
        server.quit()
        
        print(f"Email successfully sent to {user_email}")
        
    except Exception as e:
        print(f"Email Error: {e}")
        return jsonify({"status": "error", "message": "WhatsApp sent, but failed to send email receipt."}), 500

    return jsonify({"status": "success", "message": "Message sent and email receipt delivered!"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
