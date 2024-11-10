from app import db

class WarrantyCard(db.Model):
    """
    WarrantyCard model represents the warranty card details for a product.

    Attributes:
        id (int): Primary key.
        phone_number (str): Customer's phone number.
        product_name (str): Name of the product.
        purchase_date (str): Date of purchase.
        warranty_duration (str): Duration of the warranty.
        customer_name (str): Name of the customer.
        serial_number (str): Serial number of the product.
        additional_terms (str): Additional terms and conditions.
        pdf_url (str): URL to the PDF of the warranty card.
    """
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    purchase_date = db.Column(db.String(50), nullable=True)
    warranty_duration = db.Column(db.String(50), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    additional_terms = db.Column(db.Text, nullable=True)
    pdf_url = db.Column(db.String(200), nullable=True)