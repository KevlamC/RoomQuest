from flask import Blueprint
from config import get_connection

test_connection_bp = Blueprint("test_connection", __name__)

@test_connection_bp.route("/test-connection")
def test_connection():
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return "✅ Successfully connected to the database!"
        else:
            return "❌ Connection failed."
    except Exception as e:
        return f"❌ Error: {e}"
