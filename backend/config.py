import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        ssl_ca=os.getenv("SSL_CA") if os.getenv("SSL_DISABLE", "False").lower() != "true" else None,
        ssl_disabled=os.getenv("SSL_DISABLE", "False").lower() == "true"
    )
