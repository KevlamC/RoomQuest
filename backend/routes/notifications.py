from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime

notifs_bp = Blueprint("notifications", __name__)

# Insert a new notification.
@notifs_bp.route("/api/notifications/new", methods=["POST", "GET"])
def create_notification():
    data = request.get_json(silent=True) or request.args
    booking_id = data.get("bookingID")
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
    # Handles both JSON (POST) and query parameters (GET or POST with ?...)
    data = request.get_json(silent=True) or request.args

    student_id = data.get("studentID")
    club_id = data.get("clubID")

    # Convert string "true"/"false" to proper boolean
    wants_club = str(data.get("wantsClub", "true")).lower() == "true"
    wants_uni = str(data.get("wantsUniversity", "true")).lower() == "true"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO NOTIFICATION_PREFS (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              WantsClubNotifications = VALUES(WantsClubNotifications),
              WantsUniversityNotifications = VALUES(WantsUniversityNotifications)
        """, (student_id, club_id, int(wants_club), int(wants_uni)))
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

# Get all notifications for a user.
@notifs_bp.route("/api/notifications/user", methods=["GET"])
def get_all_user_notifications():
    student_id = request.args.get("studentID")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT DISTINCT n.*
            FROM NOTIFICATIONS n
            LEFT JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID
            LEFT JOIN TIME_SLOT ts ON n.BookingID = ts.BookingID
            LEFT JOIN EVENT_DETAILS ed ON ts.BookingID = ed.BookingID
            LEFT JOIN IS_MEMBER im ON im.StudentID = %s
            LEFT JOIN GETS_CLUB gc ON n.NotificationID = gc.NotificationID
            LEFT JOIN NOTIFICATION_PREFS prefs ON prefs.StudentID = %s AND prefs.ClubID = gc.ClubID
            WHERE 
                gs.StudentID = %s
                OR (n.Type = 'club_event' AND im.ClubID = gc.ClubID AND (prefs.WantsClubNotifications IS NULL OR prefs.WantsClubNotifications = TRUE))
                OR (n.Type = 'university_event' AND (prefs.WantsUniversityNotifications IS NULL OR prefs.WantsUniversityNotifications = TRUE))
            ORDER BY n.NotificationID DESC
        """, (student_id, student_id, student_id))

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get user's upcoming notifications.
@notifs_bp.route("/api/notifications/user/upcoming", methods=["GET"])
def get_upcoming_user_notifications():
    student_id = request.args.get("studentID")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.*
            FROM NOTIFICATIONS n
            JOIN TIME_SLOT ts ON n.BookingID = ts.BookingID
            LEFT JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID
            LEFT JOIN EVENT_DETAILS ed ON ts.BookingID = ed.BookingID
            LEFT JOIN IS_MEMBER im ON im.StudentID = %s
            LEFT JOIN GETS_CLUB gc ON n.NotificationID = gc.NotificationID
            LEFT JOIN NOTIFICATION_PREFS prefs ON prefs.StudentID = %s AND prefs.ClubID = gc.ClubID
            WHERE 
                ts.Date >= CURDATE()
                AND ts.Hour >= CURTIME()
                AND (
                    gs.StudentID = %s
                    OR (n.Type = 'club_event' AND im.ClubID = gc.ClubID AND (prefs.WantsClubNotifications IS NULL OR prefs.WantsClubNotifications = TRUE))
                    OR (n.Type = 'university_event' AND (prefs.WantsUniversityNotifications IS NULL OR prefs.WantsUniversityNotifications = TRUE))
                )
            ORDER BY ts.Date ASC, ts.Hour ASC
        """, (student_id, student_id, student_id))

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Notifications for a user's active/future reservations.
@notifs_bp.route("/api/notifications/user/reservations", methods=["GET"])
def get_personal_reservation_notifications():
    student_id = request.args.get("studentID")
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT n.NotificationID, n.BookingID, n.Title, n.Message, n.Type,
                   ts.Date, ts.Hour
            FROM NOTIFICATIONS n
            JOIN TIME_SLOT ts ON n.BookingID = ts.BookingID
            WHERE ts.UserID = %s AND ts.Date >= CURDATE()
            ORDER BY ts.Date ASC, ts.Hour ASC
        """, (student_id,))

        notifications = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(notifications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a specific notification.
# Delete a specific notification.
@notifs_bp.route("/api/notifications/delete", methods=["POST", "GET"])
def delete_notification():
    data = request.get_json(silent=True) or request.args
    notification_id = data.get("notificationID")
    user_id = data.get("userID")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if the notification exists
        cursor.execute("SELECT * FROM NOTIFICATIONS WHERE NotificationID = %s", (notification_id,))
        notification = cursor.fetchone()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        # Determine user type
        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_type = user["userType"]

        # Check permission
        rows_deleted = 0
        if user_type == "student":
            cursor.execute("""
                DELETE FROM GETS_STUDENT
                WHERE NotificationID = %s AND StudentID = %s
            """, (notification_id, user_id))
            rows_deleted = cursor.rowcount  # Check how many rows were affected

        elif user_type == "club":
            cursor.execute("""
                DELETE FROM GETS_CLUB
                WHERE NotificationID = %s AND ClubID = %s
            """, (notification_id, user_id))
            rows_deleted = cursor.rowcount

        elif user_type == "admin":
            cursor.execute("""
                DELETE FROM NOTIFICATIONS WHERE NotificationID = %s
            """, (notification_id,))
            rows_deleted = cursor.rowcount
        else:
            return jsonify({"error": "User type not allowed to delete notifications."}), 403

        conn.commit()
        cursor.close()
        conn.close()

        # Return a more specific message based on the result
        if rows_deleted > 0:
            return jsonify({"message": "Notification deleted (or unsubscribed)."}), 200
        else:
            return jsonify({"message": "No notifications were deleted."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete old notifications.
# Delete old notifications.
@notifs_bp.route("/api/notifications/delete-old", methods=["POST", "GET"])
def delete_old_notifications():
    data = request.get_json(silent=True) or request.args
    user_id = data.get("userID")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user type
        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_type = user["userType"]

        # Bulk delete based on date of TIME_SLOT
        rows_deleted = 0
        if user_type == "student":
            cursor.execute("""
                DELETE gs FROM GETS_STUDENT gs
                JOIN NOTIFICATIONS n ON gs.NotificationID = n.NotificationID
                JOIN TIME_SLOT ts ON n.BookingID = ts.BookingID
                WHERE gs.StudentID = %s AND ts.Date < CURDATE()
            """, (user_id,))
            rows_deleted = cursor.rowcount

        elif user_type == "club":
            cursor.execute("""
                DELETE gc FROM GETS_CLUB gc
                JOIN NOTIFICATIONS n ON gc.NotificationID = n.NotificationID
                JOIN TIME_SLOT ts ON n.BookingID = ts.BookingID
                WHERE gc.ClubID = %s AND ts.Date < CURDATE()
            """, (user_id,))
            rows_deleted = cursor.rowcount

        elif user_type == "admin":
            cursor.execute("""
                DELETE FROM NOTIFICATIONS
                WHERE BookingID IN (
                    SELECT BookingID FROM TIME_SLOT WHERE Date < CURDATE()
                )
            """)
            rows_deleted = cursor.rowcount
        else:
            return jsonify({"error": "User type not supported"}), 403

        conn.commit()
        cursor.close()
        conn.close()

        # Return a more specific message based on the result
        if rows_deleted > 0:
            return jsonify({"message": "Old notifications deleted"}), 200
        else:
            return jsonify({"message": "No old notifications to delete."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
