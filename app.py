from flask import Flask
from twilio.rest import Client
from dotenv import dotenv_values
from flask_sqlalchemy import SQLAlchemy

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