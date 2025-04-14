import os

# To import the stuff below: pip install flask flask-cors mysql-connector-python python-dotenv
# and select the global python interpreter (at least I had to do that for it to be okay).
from dotenv import load_dotenv

load_dotenv()

# Only to load database configurations from the .env file.
class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")