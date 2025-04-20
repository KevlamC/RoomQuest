from flask import Blueprint, request, jsonify
from backend.config import get_connection

features_bp = Blueprint("features", __name__)

@features_bp.route("/api/rooms/features/add", methods=["POST"])
def add_room_features():
    try:
        data = request.get_json()
        room_number = data.get("roomNumber")
        building = data.get("building")
        features = data.get("features")  # should be a list of strings

        if not room_number or not building or not features:
            return jsonify({"success": False, "error": "Missing data"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        for feature in features:
            cursor.execute("""
                INSERT IGNORE INTO FEATURES (RoomNumber, Building, Feature_Name)
                VALUES (%s, %s, %s)
            """, (room_number, building, feature))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Features added successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@features_bp.route("/api/rooms/features/delete", methods=["POST"])
def delete_room_features():
    try:
        data = request.get_json()
        room_number = data.get("roomNumber")
        building = data.get("building")
        features = data.get("features")  # should be a list of strings

        if not room_number or not building or not features:
            return jsonify({"success": False, "error": "Missing data"}), 400

        conn = get_connection()
        cursor = conn.cursor()

        for feature in features:
            cursor.execute("""
                DELETE FROM FEATURES
                WHERE RoomNumber = %s AND Building = %s AND Feature_Name = %s
            """, (room_number, building, feature))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Features deleted successfully"}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
