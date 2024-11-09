import os
from flask import request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from models import WarrantyCard
from utils import send_interactive_menu, ask_for_detail, handle_user_input, send_pdf_link
from app import app, db, PDF_FOLDER

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

with app.app_context():
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
        db.session.commit()
        db.session.add(WarrantyCard(phone_number=from_number))  # Start a new card entry
        db.session.commit()
        return "Requesting Product Name."
    elif 'view last card' in incoming_msg:
        last_card = WarrantyCard.query.filter_by(phone_number=from_number).filter(WarrantyCard.pdf_url.isnot(None)).order_by(WarrantyCard.id.desc()).first()
        if last_card:
            send_pdf_link(from_number, last_card.pdf_url)
            return "Sending PDF."
        else:
            response.message("No warranty card found.")
            return str(response)
    else:
        handle_user_input(from_number, incoming_msg)
        return "Handling user input."

@app.route('/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
