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

# Enable CORS so your React frontend (e.g., localhost:5173 or your Vercel/Netlify domain) can talk to Flask
CORS(app)

# --- Twilio Credentials ---
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886' 
COMPANY_WHATSAPP_TO = 'whatsapp:+919486802976'

# Initialize Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# --- Email Credentials ---
SENDER_EMAIL = os.getenv('SENDER_EMAIL')      
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') 

# ---------------------------------------------------------
# ROOT ROUTE (Health Check for Render)
# ---------------------------------------------------------
@app.route('/')
def home():
    # Returns a simple JSON response for Render's health checks
    return jsonify({
        "status": "online", 
        "service": "Eemon X Backend API",
        "message": "System operational and ready to receive transmissions."
    }), 200

# ---------------------------------------------------------
# FORM SUBMISSION API ENDPOINT
# ---------------------------------------------------------
@app.route('/send-whatsapp', methods=['POST'])
def process_form():
    data = request.json
    
    # Extract data from the frontend form
    name = data.get('name', 'N/A')
    phone = data.get('phone', 'N/A')
    user_email = data.get('email', 'N/A')
    service = data.get('service', 'N/A')
    user_message = data.get('message', 'N/A')

    # 1. SEND WHATSAPP TO EEMON X TEAM
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
        print(f"WhatsApp sent successfully. SID: {msg.sid}")
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return jsonify({"status": "error", "message": "Failed to send WhatsApp alert to the team."}), 500

    # 2. SEND AUTO-REPLY EMAIL TO THE USER
    email_subject = f"Transmission Received: Welcome to Eemon X, {name}"
    
    email_body = f"""Hi {name},

Thank you for initializing a connection with Eemon X. We have successfully received your inquiry regarding {service}.

Here is a secure log of the details you transmitted:
-------------------------------------------------
Name: {name}
Phone: {phone}
Email: {user_email}
Service Required: {service}

Your Message:
{user_message}
-------------------------------------------------

Our board members will review your requirements, and a specialist will deploy a response to you shortly.

Best regards,
The Eemon X Team
Securing the future, designing the present.
Official Comms: eemonx2025@gmail.com
"""

    try:
        email_msg = MIMEMultipart()
        email_msg['From'] = f"Eemon X <{SENDER_EMAIL}>"
        email_msg['To'] = user_email
        email_msg['Subject'] = email_subject
        email_msg.attach(MIMEText(email_body, 'plain'))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(email_msg)
        server.quit()
        
        print(f"Email successfully sent to {user_email}")
        
    except Exception as e:
        print(f"Email Error: {e}")
        return jsonify({"status": "error", "message": "WhatsApp sent, but failed to send email receipt to the user."}), 500

    # If both succeed
    return jsonify({"status": "success", "message": "Transmission Successful. Protocol Initiated."}), 200

# ---------------------------------------------------------
# SERVER INITIALIZATION
# ---------------------------------------------------------
if __name__ == '__main__':
    # Grab the port from Render's environment, default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    
    # host='0.0.0.0' explicitly exposes the app to the public internet
    # debug=False is required for production environments
    app.run(host='0.0.0.0', port=port, debug=False)
