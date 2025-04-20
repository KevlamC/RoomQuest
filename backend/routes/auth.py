from flask import Blueprint, request, jsonify
from backend.config import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "success": False,
                "message": "Missing email or password.",
                "email": email,
                "password": password
            }), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT ID, Email, Username, Password, userType FROM USER WHERE Email = %s", (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["Password"] == password:
            return jsonify({
                "success": True,
                "message": "Login successful.",
                "userId": user["ID"],
                "username": user["Username"],
                "userType": user["userType"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Invalid credentials."
            }), 401

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
