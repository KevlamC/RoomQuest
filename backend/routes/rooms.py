from flask import Blueprint, request, jsonify

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/search", methods=["GET"])
def search_rooms():
    building = request.args.get("building", default="EDC")

    try:
        # TODO: Uncomment and use actual DB queries when ready
        # conn = get_db_connection()
        # cursor = conn.cursor(dictionary=True)
        # cursor.execute("SELECT * FROM rooms WHERE building = %s", (building,))
        # results = cursor.fetchall()
        # cursor.close()
        # conn.close()
        # return jsonify(results), 200

        # Dummy test data
        return jsonify([{"room": "EDC 101"}, {"room": "EDC 202"}]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
