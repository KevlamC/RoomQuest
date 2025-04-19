from flask import Blueprint, request, jsonify
from backend.config import get_connection  # Make sure this is imported

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/search", methods=["GET"])
def search_rooms():
    building = request.args.get("building", default="EDC")  # Optional, currently unused

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Since we don't yet have a 'building' column, just return all rooms
        cursor.execute("SELECT * FROM rooms;")
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rooms_bp.route("/test", methods=["GET"])
def test_rooms():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM rooms;")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify(rows), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
