from flask import Blueprint, jsonify
from backend.config import get_connection

user_list_bp = Blueprint("user_list", __name__)

@user_list_bp.route("/api/users/all", methods=["GET"])
def get_all_users():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email FROM USER")  # Using actual table name
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "users": users}), 200  # Use the correct variable name
    except Exception as e:
        print("Error fetching users:", e)
        return jsonify({"success": False, "message": str(e)}), 500
