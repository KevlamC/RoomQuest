from flask import Blueprint, jsonify
from config import get_connection

test_connection_bp = Blueprint("test_connection", __name__)

@test_connection_bp.route("/test-connection")
def test_connection():
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return jsonify({"status": "ok", "db": "connected"}), 200
        else:
            return jsonify({"status": "error", "db": "not connected"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
