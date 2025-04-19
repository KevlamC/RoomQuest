from flask import Blueprint, jsonify
from backend.config import get_connection

notifs_bp = Blueprint("notifs", __name__)

@notifs_bp.route("/api/user/<int:user_id>/notifications", methods=["GET"])
def get_user_notifications(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get all notifications tied to user's bookings
        cursor.execute("""
            SELECT n.Title, n.Message, n.Type
            FROM NOTIFICATIONS n
            JOIN TIME_SLOT t ON n.BookingID = t.BookingID
            WHERE t.UserID = %s
            ORDER BY n.NotificationID DESC
        """, (user_id,))

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "notifications": notifications
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500