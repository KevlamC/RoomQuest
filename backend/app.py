from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()  # Loads from root .env

# Create Flask app instance
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add this at the bottom of the file
if __name__ == '__main__':
    app.run(debug=True)