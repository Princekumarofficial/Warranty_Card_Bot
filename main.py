import os
import uuid
from dotenv import dotenv_values
from flask import Flask, request, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from weasyprint import HTML

app = Flask(__name__)

# Load config from .env
config = dotenv_values(".env")
TWILIO_ACCOUNT_SID = config["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = config["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_NUMBER = f'whatsapp:{config["TWILIO_WHATSAPP_NUMBER"]}'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Set up database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create directory for temporary PDFs
PDF_FOLDER = 'pdfs'
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

# Database model for warranty cards
class WarrantyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    purchase_date = db.Column(db.String(50), nullable=False)
    warranty_duration = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)
    additional_terms = db.Column(db.Text, nullable=True)
    pdf_url = db.Column(db.String(200), nullable=False)

db.create_all()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get('From')
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()

    if 'hi' in incoming_msg:
        send_interactive_menu(from_number)
        return "Interactive menu sent."
    elif 'create new' in incoming_msg:
        ask_for_detail(from_number, "Product Name")
        db.session.query(WarrantyCard).filter(WarrantyCard.phone_number == from_number).delete()  # Clear existing data
        db.session.commit()
        db.session.add(WarrantyCard(phone_number=from_number))  # Start a new card entry
        db.session.commit()
        return "Requesting Product Name."
    elif 'view last card' in incoming_msg:
        last_card = WarrantyCard.query.filter_by(phone_number=from_number).order_by(WarrantyCard.id.desc()).first()
        if last_card:
            send_pdf_link(from_number, last_card.pdf_url)
            return "Sending PDF."
        else:
            response.message("No warranty card found.")
            return str(response)
    else:
        handle_user_input(from_number, incoming_msg)
        return "Handling user input."

def send_interactive_menu(to_number):
    client.messages.create(
        content_sid="HX708ef706226c99a481d82c8a48fc416a",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number,
    )

def ask_for_detail(to_number, detail_name):
    client.messages.create(
        body=f"Please enter the {detail_name}:",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )

def handle_user_input(from_number, incoming_msg):
    # Fields to be filled in sequence
    detail_sequence = ["product_name", "purchase_date", "warranty_duration", 
                       "customer_name", "serial_number", "additional_terms"]

    card = WarrantyCard.query.filter_by(phone_number=from_number).first()
    if card:
        for field in detail_sequence:
            if not getattr(card, field):  # Check if field is empty
                setattr(card, field, incoming_msg.upper())
                db.session.commit()
                next_index = detail_sequence.index(field) + 1
                if next_index < len(detail_sequence):
                    ask_for_detail(from_number, detail_sequence[next_index].replace("_", " ").capitalize())
                else:
                    pdf_filename = generate_pdf(card)
                    pdf_url = request.url_root + 'pdfs/' + pdf_filename
                    card.pdf_url = pdf_url
                    db.session.commit()
                    send_pdf_link(from_number, pdf_url)
                return
    else:
        ask_for_detail(from_number, "Product Name")

def generate_pdf(card):
    rendered_html = render_template("warranty_card.html", details=card)
    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

    HTML(string=rendered_html).write_pdf(pdf_path)
    return pdf_filename

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)

def send_pdf_link(to_number, pdf_url):
    client.messages.create(
        body="Here is your warranty card PDF:",
        media_url=pdf_url,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )

if __name__ == "__main__":
    app.run(port=8000, debug=True)
