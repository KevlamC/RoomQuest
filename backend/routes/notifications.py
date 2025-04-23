from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime

notifs_bp = Blueprint("notifications", __name__)


# General entrypoint for all booking-approval notifications.
@notifs_bp.route("/api/notification/general-to-all", methods=["POST", "GET"])
def notification_general_function():
    """
    General entrypoint for all booking‐approval notifications.
    Expects (as JSON or form/query params):
      - BookingID (int)
      - approved  (true|false)
    """
    try:
        if request.method == "POST":
            booking_id = request.values.get("BookingID", type=int)
            approved = str(request.values.get("approved", "")).lower() == "true"
        elif request.method == "GET":
            booking_id = request.args.get("BookingID", type=int)
            approved = str(request.args.get("approved", "")).lower() == "true"

        if not booking_id:
            return jsonify(success=False, message="Missing BookingID"), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # 1) Load the booking to inspect its type, user, date, hour…
        cur.execute("""
            SELECT ts.BookingID, ts.UserID, ts.Date, ts.Hour, ts.Duration, ts.BookingType, ts.IsApproved,
                   r.Building, r.RoomNumber
            FROM TIME_SLOT ts
            JOIN ROOMS r ON r.RoomNumber = ts.RoomNumber AND r.Building = ts.Building
            WHERE ts.BookingID = %s
        """, (booking_id,))
        booking = cur.fetchone()
        if not booking:
            cur.close(); conn.close()
            return jsonify(success=False, message="Booking not found"), 404

        # 2) Dispatch based on BookingType
        bt = booking["BookingType"]
        if bt == "student" and approved:
            notify_student_booking(cur, booking)
        elif bt == "club" and approved:
            notify_club_booking(cur, booking)
        elif bt == "student" and not approved:
            notify_student_booking_rejected(cur, booking)
        elif bt == "club" and not approved:
            notify_club_booking_rejected(cur, booking)
        else:
            pass

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(
            success=True,
            message=f"Notification(s) created for {bt} booking #{booking_id}"
        ), 200

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


def notify_student_booking(cur, booking):
    
    title = f"Booking Confirmed: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been approved."

    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_approved')
    """, (booking["BookingID"], title, message))

    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()["LAST_INSERT_ID()"]

    cur.execute("""
        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))


def notify_club_booking(cur, booking):
    title = f"Booking Confirmed: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been approved."

    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_approved')
    """, (booking["BookingID"], title, message))

    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()["LAST_INSERT_ID()"]

    cur.execute("""
        INSERT INTO GETS_CLUB (NotificationID, ClubID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))


def notify_student_booking_rejected(cur, booking):
    title = f"Booking Rejected: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been rejected."

    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_rejected')
    """, (booking["BookingID"], title, message))

    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()["LAST_INSERT_ID()"]

    cur.execute("""
        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))

def notify_club_booking_rejected(cur, booking):
    title = f"Booking Rejected: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your club's room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been rejected."

    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_rejected')
    """, (booking["BookingID"], title, message))

    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()["LAST_INSERT_ID()"]

    cur.execute("""
        INSERT INTO GETS_CLUB (NotificationID, ClubID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))



def notify_club_event(cur, booking):
    """
    Notifies all student members of the club that is hosting a newly approved club event,
    filtered by their event topic preferences.
    """
    # Step 1: Get ClubID for the event
    cur.execute("""
        SELECT ClubID FROM EVENT_DETAILS
        WHERE BookingID = %s AND EventType = 'club'
    """, (booking["BookingID"],))
    result = cur.fetchone()

    if not result or not result["ClubID"]:
        return  # No club found for this event — exit silently for now

    club_id = result["ClubID"]

    # Step 2: Insert notification into NOTIFICATIONS
    title = f"New Club Event: {booking['Date']} at {booking['Hour']} in {booking['Building']} {booking['RoomNumber']}"
    message = f"A new event hosted by your club is scheduled for {booking['Date']} at {booking['Hour']} in {booking['Building']} {booking['RoomNumber']}."

    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'club_event')
    """, (booking["BookingID"], title, message))

    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()["LAST_INSERT_ID()"]

    # Step 3: Notify only student members of the club who have opted into at least one of the event's topics
    cur.execute("""
        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
        SELECT DISTINCT %s AS NotificationID, prefs.UserID
        FROM EVENT_TOPICS et
        JOIN USER_EVENT_TOPIC_PREFS prefs ON et.Topic = prefs.Topic
        JOIN IS_MEMBER m ON prefs.UserID = m.StudentID
        WHERE et.BookingID = %s AND m.ClubID = %s
    """, (notification_id, booking["BookingID"], club_id))



# Get all notifications for a user (GET).
@notifs_bp.route("/api/notifications/user", methods=["GET"])
def get_all_user_notifications():
    try:
        cur.execute("DELETE * FROM NOTIFICATIONS WHERE BookingID IS NULL")

        user_id = request.args.get("user_id", type=int)
        user_type = request.args.get("user_type", type=str)

        if not user_id or user_type not in ("student", "club"):
            return jsonify(success=False, message="Missing or invalid user_id or user_type"), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        if user_type == "student":
            notifications = get_all_student_notifications(cur, user_id)
        else:
            notifications = get_all_club_notifications(cur, user_id)

        cur.close()
        conn.close()

        return jsonify(success=True, notifications=notifications), 200

    except Exception as e:
        return jsonify(success=False, message=str(e)), 500


def get_all_student_notifications(cur, user_id):
    cur.execute("""
        SELECT N.NotificationID, N.BookingID, N.Title, N.Message, N.Type
        FROM NOTIFICATIONS N
        JOIN GETS_STUDENT GS ON N.NotificationID = GS.NotificationID
        WHERE GS.StudentID = %s
        AND N.Type IN ('booking_approved', 'booking_cancelled', 'club_event')
        ORDER BY N.NotificationID DESC
    """, (user_id,))
    return cur.fetchall()


def get_all_club_notifications(cur, user_id):
    cur.execute("""
        SELECT N.NotificationID, N.BookingID, N.Title, N.Message, N.Type
        FROM NOTIFICATIONS N
        JOIN GETS_CLUB GC ON N.NotificationID = GC.NotificationID
        WHERE GC.ClubID = %s
          AND N.Type IN ('booking_approved', 'booking_cancelled', 'club_event')
        ORDER BY N.NotificationID DESC
    """, (user_id,))
    return cur.fetchall()


# Get user's upcoming notifications (GET).
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
            LEFT JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID AND gs.StudentID = %s
            LEFT JOIN EVENT_DETAILS ed ON ts.BookingID = ed.BookingID
            LEFT JOIN IS_MEMBER im ON im.StudentID = %s
            LEFT JOIN GETS_CLUB gc ON n.NotificationID = gc.NotificationID
            LEFT JOIN NOTIFICATION_PREFS prefs ON prefs.StudentID = %s AND prefs.ClubID = gc.ClubID
            WHERE 
                ts.Date >= CURDATE()
                AND ts.Hour >= CURTIME()
                AND (
                    gs.StudentID IS NOT NULL
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


# Delete a specific notification (POST and GET).
@notifs_bp.route("/api/notifications/delete", methods=["POST", "GET"])
def delete_notification():
    data = request.get_json(silent=True) or request.args
    notification_id = data.get("notificationID")
    user_id = data.get("userID")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM NOTIFICATIONS WHERE NotificationID = %s", (notification_id,))
        notification = cursor.fetchone()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_type = user["userType"]
        rows_deleted = 0

        if user_type == "student":
            cursor.execute("""
                DELETE FROM GETS_STUDENT
                WHERE NotificationID = %s AND StudentID = %s
            """, (notification_id, user_id))
            rows_deleted = cursor.rowcount
        elif user_type == "club":
            cursor.execute("""
                DELETE FROM GETS_CLUB
                WHERE NotificationID = %s AND ClubID = %s
            """, (notification_id, user_id))
            rows_deleted = cursor.rowcount
        else:
            return jsonify({"error": "User type not allowed to delete notifications."}), 403

        conn.commit()
        cursor.close()
        conn.close()

        if rows_deleted > 0:
            return jsonify({"message": "Notification deleted (or unsubscribed)."}), 200
        else:
            return jsonify({"message": "No notifications were deleted."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
