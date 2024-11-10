from app import db, TWILIO_WHATSAPP_NUMBER, client, PDF_FOLDER
from flask import render_template, request
from weasyprint import HTML
import os
import uuid
from models import WarrantyCard

def send_interactive_menu(to_number):
    """
    Sends an interactive menu to the specified WhatsApp number.
    
    Args:
        to_number (str): The recipient's WhatsApp number.
    """
    client.messages.create(
        content_sid="HX708ef706226c99a481d82c8a48fc416a",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number,
    )

def ask_for_detail(to_number, detail_name):
    """
    Asks the user for a specific detail via WhatsApp message.
    
    Args:
        to_number (str): The recipient's WhatsApp number.
        detail_name (str): The name of the detail to ask for.
    """
    client.messages.create(
        body=f"Please enter the {detail_name}:",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )

def handle_user_input(from_number, incoming_msg):
    """
    Handles user input and updates the warranty card details.
    
    Args:
        from_number (str): The sender's WhatsApp number.
        incoming_msg (str): The incoming message content.
    """
    detail_sequence = ["product_name", "purchase_date", "warranty_duration", 
                       "customer_name", "serial_number", "additional_terms"]

    card = WarrantyCard.query.filter_by(phone_number=from_number).order_by(WarrantyCard.id.desc()).first()
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
    """
    Generates a PDF for the warranty card.
    
    Args:
        card (WarrantyCard): The warranty card object.
    
    Returns:
        str: The filename of the generated PDF.
    """
    card_details = {
        "product_name": card.product_name,
        "purchase_date": card.purchase_date,
        "warranty_duration": card.warranty_duration,
        "customer_name": card.customer_name,
        "phone_number": card.phone_number,
        "serial_number": card.serial_number,
        "additional_terms": card.additional_terms
    }

    rendered_html = render_template("warranty_card.html", details=card_details)
    pdf_filename = f"{uuid.uuid4()}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)

    HTML(string=rendered_html).write_pdf(pdf_path)
    return pdf_filename

def send_pdf_link(to_number, pdf_url):
    """
    Sends the PDF link to the specified WhatsApp number.
    
    Args:
        to_number (str): The recipient's WhatsApp number.
        pdf_url (str): The URL of the PDF.
    """
    client.messages.create(
        body="Here is your warranty card PDF:",
        media_url=pdf_url,
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )
