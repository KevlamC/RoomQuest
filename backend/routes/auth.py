from flask import Blueprint, request, jsonify
import mysql.connector  # or your preferred connector
from backend.config import get_connection  # Make sure this is imported

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("Email")
        password = data.get("Password")

        if not email or not password:
            return jsonify({"success": False, "message": "Missing email or password."}), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT Email, Password FROM USER WHERE Email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["Password"] == password:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Invalid credentials."}), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
