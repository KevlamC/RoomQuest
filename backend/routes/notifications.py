from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime, timedelta

notifs_bp = Blueprint("notifications", __name__)

# Insert a new notification.
@notifs_bp.route("/api/notifications/new", methods=["POST", "GET"])
def create_notification():
    data = request.get_json()
    booking_id = data.get("bookingid")
    title = data.get("title")
    message_r = data.get("message")
    notif_type = data.get("type")  # 'booking_approved', 'club_event', etc.

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, title, message_r, notif_type))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            "message": "Notification created successfully",
            "notification": {
                "bookingID": booking_id,
                "title": title,
                "message": message_r,
                "type": notif_type
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update user notification preferences.
@notifs_bp.route("/api/notifications/prefs", methods=["POST", "GET"])
def update_prefs():
    data = request.get_json()
    student_id = data.get("studentID")
    club_id = data.get("clubID")
    wants_club = data.get("wantsClub", True)
    wants_uni = data.get("wantsUniversity", True)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NOTIFICATION_PREFS (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              WantsClubNotifications = VALUES(WantsClubNotifications),
              WantsUniversityNotifications = VALUES(WantsUniversityNotifications)
        """, (student_id, club_id, wants_club, wants_uni))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({
            "message": "Preferences updated",
            "preferences": {
                "studentID": student_id,
                "clubID": club_id,
                "wantsClub": wants_club,
                "wantsUniversity": wants_uni
            }
        }), 200
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
@notifs_bp.route("/api/notifications/delete", methods=["POST", "GET"])
def delete_notification():
    data = request.get_json()
    notif_id = data.get("notificationID")
    cutoff = data.get("cutoffDate")  # optional YYYY-MM-DD

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if notif_id:
            cursor.execute("DELETE FROM NOTIFICATIONS WHERE NotificationID = %s", (notif_id,))
        elif cutoff:
            cursor.execute("DELETE FROM NOTIFICATIONS WHERE DATE(BookingID) < %s", (cutoff,))
        else:
            return jsonify({"error": "Provide notificationID or cutoffDate"}), 400

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Notification(s) deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500