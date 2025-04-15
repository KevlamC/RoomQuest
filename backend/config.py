import os

# To import the stuff below: pip install flask flask-cors mysql-connector-python python-dotenv
# and select the global python interpreter (at least I had to do that for it to be okay).
from dotenv import load_dotenv

load_dotenv()

# Only to load database configurations from the .env file.
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=3306
    )
