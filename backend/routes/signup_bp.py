# routes/signup_route.py
from flask import Blueprint, request, jsonify
from backend.config import get_connection

signup_bp = Blueprint("signup", __name__)

@signup_bp.route("/api/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        user_id = data.get("id")
        email = data.get("email")
        username = data.get("username")  # ✅ new field from frontend
        password = data.get("password")

        if not all([user_id, email, username, password]):
            return jsonify({"success": False, "message": "Missing fields"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Insert into USER table
        cursor.execute("""
            INSERT INTO USER (ID, Email, Username, Password)
            VALUES (%s, %s, %s, %s)
        """, (user_id, email, username, password))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
