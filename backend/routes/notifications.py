from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime

notifs_bp = Blueprint("notifications", __name__)


@notifs_bp.route("/api/notification/general-to-all", methods=["POST"])
def notification_general_function():
    """
    General entrypoint for all booking‐approval notifications.
    Expects (as JSON or form/query params):
      - BookingID (int)
      - approved  (true|false)
    """
    try:
        booking_id = request.values.get("BookingID", type=int)
        # ----------------------------
        approved   = str(request.values.get("approved", "")).lower() == "true"
        # ----------------------------

        if not booking_id:
            return jsonify(success=False, message="Missing BookingID"), 400

        conn = get_connection()
        cur  = conn.cursor(dictionary=True)

        # 1) Load the booking to inspect its type, user, date, hour…
        cur.execute("""
            SELECT BookingID, UserID, Date, Hour, Duration, BookingType, IsApproved
            FROM TIME_SLOT
            WHERE BookingID = %s
        """, (booking_id,))
        booking = cur.fetchone()
        if not booking:
            cur.close(); conn.close()
            return jsonify(success=False, message="Booking not found"), 404

        # 2) Dispatch based on BookingType
        bt = booking["BookingType"]
        approval = booking["IsApproved"]
        if bt == "student" and approved:
            notify_student_booking(cur, booking)
        elif bt == "club" and approved:
            notify_club_booking(cur, booking)
        # elif bt == "group" and approved:
            # notify_group_booking(cur, booking)
        elif bt == "student" and not approved:
            notify_student_booking_rejected(cur, booking)
        elif bt = "club" and not approved:
            notify_club_booking_rejected(cur, booking)
        # elif bt = "club_event" and approved:
            # notify_club_event(cur, booking)
        # elif bt = "university_event" and approved:
            # notiy_university_event(cur, booking)
        else:
            # extend for 'admin', 'university_event', etc.
            pass

        # 3) Commit once after helper(s) insert NOTIFICATIONS & GETS_*
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
    
    # Prepare title and message
    title = f"Booking Confirmed: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been approved."
    
    # Insert into NOTIFICATIONS
    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_approved')
    """, (booking["BookingID"], title, message))

    # Get the NotificationID of the inserted notification
    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()[0]

    # Insert into GETS_STUDENT
    cur.execute("""
        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))



def notify_club_booking(cur, booking):
    
    # Prepare title and message
    title = f"Booking Confirmed: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been approved."
    
    # Insert into NOTIFICATIONS
    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_approved')
    """, (booking["BookingID"], title, message))

    # Get the NotificationID of the inserted notification
    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()[0]

    # Insert into GETS_CLUB
    cur.execute("""
        INSERT INTO GETS_CLUB (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))


def notify_student_booking_rejected(cur, booking):
    # Prepare title and message
    title = f"Booking Rejected: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been rejected."

    # Insert into NOTIFICATIONS
    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_rejected')
    """, (booking["BookingID"], title, message))

    # Get the NotificationID of the inserted notification
    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()[0]

    # Insert into GETS_STUDENT
    cur.execute("""
        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))


def notify_club_booking_rejected(cur, booking):
    # Prepare title and message
    title = f"Booking Rejected: {booking['Building']} {booking['RoomNumber']}, {booking['Date']} at {booking['Hour']}"
    message = f"Your club's room booking for {booking['RoomNumber']} in {booking['Building']} on {booking['Date']} at {booking['Hour']} has been rejected."

    # Insert into NOTIFICATIONS
    cur.execute("""
        INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
        VALUES (%s, %s, %s, 'booking_rejected')
    """, (booking["BookingID"], title, message))

    # Get the NotificationID of the inserted notification
    cur.execute("SELECT LAST_INSERT_ID()")
    notification_id = cur.fetchone()[0]

    # Insert into GETS_CLUB
    cur.execute("""
        INSERT INTO GETS_CLUB (NotificationID, StudentID)
        VALUES (%s, %s)
    """, (notification_id, booking["UserID"]))















# Insert a new notification.
@notifs_bp.route("/api/notifications/new", methods=["POST", "GET"])
def create_notification():
    data = request.get_json(silent=True) or request.args
    booking_id = data.get("bookingID")
    title = data.get("title")
    message_r = data.get("message")
    notif_type = data.get("type")  # 'booking_approved', 'club_event', 'university_event', etc.

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Insert notification
        cursor.execute("""
            INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, title, message_r, notif_type))
        notification_id = cursor.lastrowid

        if notif_type == "club_event":
            # Get ClubID from EVENT_DETAILS
            cursor.execute("""
                SELECT ClubID FROM EVENT_DETAILS WHERE BookingID = %s
            """, (booking_id,))
            club_row = cursor.fetchone()

            if club_row:
                club_id = club_row["ClubID"]

                # Get all StudentIDs who are members AND want notifications (or no preference set)
                cursor.execute("""
                    SELECT im.StudentID
                    FROM IS_MEMBER im
                    LEFT JOIN NOTIFICATION_PREFS np 
                      ON im.StudentID = np.StudentID AND np.ClubID = %s
                    WHERE im.ClubID = %s
                      AND (np.WantsClubNotifications IS NULL OR np.WantsClubNotifications = TRUE)
                """, (club_id, club_id))
                student_rows = cursor.fetchall()

                if student_rows:
                    values = [(notification_id, row["StudentID"]) for row in student_rows]
                    cursor.executemany("""
                        INSERT INTO GETS_STUDENT (NotificationID, StudentID)
                        VALUES (%s, %s)
                    """, values)

        elif notif_type == "university_event":
            # Notify students who opted in to university notifications
            cursor.execute("""
                SELECT StudentID FROM NOTIFICATION_PREFS
                WHERE WantsUniversityNotifications = TRUE
            """)
            student_rows = cursor.fetchall()

            if student_rows:
                values = [(notification_id, row["StudentID"]) for row in student_rows]
                cursor.executemany("""
                    INSERT INTO GETS_STUDENT (NotificationID, StudentID)
                    VALUES (%s, %s)
                """, values)

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
    data = request.get_json(silent=True) or request.args

    student_id = data.get("studentID")
    club_id = data.get("clubID")

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
            LEFT JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID AND gs.StudentID = %s
            LEFT JOIN EVENT_DETAILS ed ON n.BookingID = ed.BookingID
            LEFT JOIN IS_MEMBER im ON im.StudentID = %s
            LEFT JOIN GETS_CLUB gc ON n.NotificationID = gc.NotificationID
            LEFT JOIN NOTIFICATION_PREFS prefs ON prefs.StudentID = %s AND prefs.ClubID = gc.ClubID
            WHERE 
                gs.StudentID IS NOT NULL
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

        if rows_deleted > 0:
            return jsonify({"message": "Notification deleted (or unsubscribed)."}), 200
        else:
            return jsonify({"message": "No notifications were deleted."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete old notifications.
@notifs_bp.route("/api/notifications/delete-old", methods=["POST", "GET"])
def delete_old_notifications():
    data = request.get_json(silent=True) or request.args
    user_id = data.get("userID")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_type = user["userType"]
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

        if rows_deleted > 0:
            return jsonify({"message": "Old notifications deleted"}), 200
        else:
            return jsonify({"message": "No old notifications to delete."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
