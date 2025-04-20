from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime, timedelta

notifs_bp = Blueprint("notifications", __name__)

# Insert a new notification.
@notifs_bp.route("/api/notifications/new", methods=["GET", "POST"])
def create_notification():
    if request.method == "GET":
        # Pull query params if provided
        booking_id = request.args.get("bookingid")
        title = request.args.get("title")
        message = request.args.get("message")
        notif_type = request.args.get("type")

        if booking_id and title and message and notif_type:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
                    VALUES (%s, %s, %s, %s)
                """, (booking_id, title, message, notif_type))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({
                    "message": "Notification created via GET!",
                    "bookingid": booking_id,
                    "title": title,
                    "text": message,
                    "type": notif_type
                }), 201
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({
                "message": "Use GET with all query parameters: bookingid, title, message, type."
            }), 400

    # POST method
    data = request.get_json()
    booking_id = data.get("bookingid")
    title = data.get("title")
    message = data.get("message")
    notif_type = data.get("type")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, title, message, notif_type))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Notification created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update user notification preferences.
@notifs_bp.route("/api/notifications/prefs", methods=["GET", "POST"])
def update_preferences():
    if request.method == "GET":
        user_id = request.args.get("userid")
        notif_type = request.args.get("type")
        enabled = request.args.get("enabled")

        if user_id and notif_type and enabled:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO NOTIFICATION_PREFS (UserID, Type, Enabled)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE Enabled = VALUES(Enabled)
                """, (user_id, notif_type, enabled))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({
                    "message": "Preferences updated via GET!",
                    "userid": user_id,
                    "type": notif_type,
                    "enabled": enabled
                }), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({
                "message": "Use GET with query params: userid, type, enabled"
            }), 400

    # POST version
    data = request.get_json()
    user_id = data.get("userid")
    notif_type = data.get("type")
    enabled = data.get("enabled")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NOTIFICATION_PREFS (UserID, Type, Enabled)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Enabled = VALUES(Enabled)
        """, (user_id, notif_type, enabled))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Preferences updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all notifications for a student (personalized).
@notifs_bp.route("/api/notifications/user", methods=["GET"])
def get_user_notifications():
    student_id = request.args.get("studentID")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT n.*
            FROM NOTIFICATIONS n
            JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID
            WHERE gs.StudentID = %s
            ORDER BY n.NotificationID DESC
        """, (student_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get club/university notifications user is subscribed to.
@notifs_bp.route("/api/notifications/general", methods=["GET"])
def get_general_notifications():
    student_id = request.args.get("studentID")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT n.*
            FROM NOTIFICATIONS n
            JOIN GETS_CLUB gc ON n.NotificationID = gc.NotificationID
            JOIN NOTIFICATION_PREFS np ON gc.ClubID = np.ClubID AND np.StudentID = %s
            WHERE (n.Type = 'club_event' AND np.WantsClubNotifications = TRUE)
               OR (n.Type = 'university_event' AND np.WantsUniversityNotifications = TRUE)
            ORDER BY n.NotificationID DESC
        """, (student_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Notifications for a user's active/future reservations.
@notifs_bp.route("/api/notifications/reservations", methods=["GET"])
def get_reservation_notifications():
    student_id = request.args.get("studentID")
    today = datetime.now().date()

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.*
            FROM NOTIFICATIONS n
            JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID
            JOIN TIME_SLOT t ON n.BookingID = t.BookingID
            WHERE gs.StudentID = %s
              AND t.Date >= %s
              AND t.BookingType = 'student'
            ORDER BY t.Date, t.Hour
        """, (student_id, today))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a specific notification or clean old ones.
@notifs_bp.route("/api/notifications/delete", methods=["GET", "DELETE"])
def delete_notification():
    if request.method == "GET":
        notif_id = request.args.get("id")
        if notif_id:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM NOTIFICATIONS WHERE ID = %s", (notif_id,))
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({
                    "message": f"Notification {notif_id} deleted via GET"
                }), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        else:
            return jsonify({
                "message": "Use GET with query param ?id=<notification_id>"
            }), 400

    # DELETE version
    data = request.get_json()
    notif_id = data.get("id")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM NOTIFICATIONS WHERE ID = %s", (notif_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Notification deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
