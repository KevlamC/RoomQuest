from flask import Blueprint, jsonify
from backend.config import get_connection

points = Blueprint("totalPoints", __name__)

@points.route("/api/user/<int:user_id>/points", methods=["GET"])
def get_user_points(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_type = user["userType"]
        if user_type == "student":
            cursor.execute("SELECT Points FROM STUDENT WHERE ID = %s", (user_id,))
        elif user_type == "club":
            cursor.execute("SELECT Points FROM CLUB WHERE ID = %s", (user_id,))
        else:
            return jsonify({"userType": user_type})

        points = cursor.fetchone()
        cursor.close()
        conn.close()

        return jsonify({
            "userId": user_id,
            "userType": user_type,
            "points": points["Points"] if points else 0
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
