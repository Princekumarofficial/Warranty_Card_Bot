from app import db

class WarrantyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), nullable=True)
    product_name = db.Column(db.String(100), nullable=True)
    purchase_date = db.Column(db.String(50), nullable=True)
    warranty_duration = db.Column(db.String(50), nullable=True)
    customer_name = db.Column(db.String(100), nullable=True)
    serial_number = db.Column(db.String(100), nullable=True)
    additional_terms = db.Column(db.Text, nullable=True)
    pdf_url = db.Column(db.String(200), nullable=True)