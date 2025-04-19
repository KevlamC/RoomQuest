from flask import Blueprint, jsonify
from backend.config import get_connection

reservUpcoming = Blueprint("reservUpcoming", __name__)

@reservUpcoming.route("/api/user/<int:user_id>/reservations", methods=["GET"])
def get_user_upcoming_reservations(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL Query 
        cursor.execute("""
            SELECT 
                RoomNumber,
                Building,
                Date,
                Hour AS time,
                Duration
            FROM TIME_SLOT
            WHERE UserID = %s
              AND Date >= CURDATE()
              AND IsApproved = TRUE
            ORDER BY Date ASC, Hour ASC
            LIMIT 3
        """, (user_id,))

        reservations = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "reservations": reservations
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500