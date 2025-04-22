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





# Update user notification preferences (POST and GET).
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


@notifs_bp.route("/api/notifications/user", methods=["GET"])
def get_all_user_notifications():
    """
    Returns notifications for a given user, filtered by:
      • booking_approved & booking_cancelled always included
      • club_event included only if:
          – global WantsClubNotifications = TRUE
          – AND per‑club WantsThisClubNotifications = TRUE
      • university_event included only if:
          – global WantsUniversityNotifications = TRUE
          – AND per‑topic WantsNotification = TRUE
    """
    user_id = request.args.get("userID", type=int)
    if not user_id:
        return jsonify(success=False, message="Missing userID"), 400

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # 1) Load global prefs
    cur.execute("""
        SELECT WantsClubNotifications, WantsUniversityNotifications
        FROM NOTIFICATION_PREFS
        WHERE UserID = %s
    """, (user_id,))
    prefs = cur.fetchone() or {"WantsClubNotifications": True,
                                "WantsUniversityNotifications": True}
    want_clubs = bool(prefs["WantsClubNotifications"])
    want_unis = bool(prefs["WantsUniversityNotifications"])

    # 2) Load raw notifications (via GETS_STUDENT or GETS_CLUB)
    #    We’ll treat everyone as a student here—adjust if clubs differ.
    cur.execute("""
        SELECT n.NotificationID, n.BookingID, n.Title, n.Message, n.Type
        FROM NOTIFICATIONS n
        JOIN GETS_STUDENT gs ON n.NotificationID = gs.NotificationID
        WHERE gs.StudentID = %s
        ORDER BY n.NotificationID DESC
    """, (user_id,))
    raw = cur.fetchall()

    filtered = []
    for n in raw:
        t = n["Type"]

        # — Always keep booking_approved & booking_cancelled —
        if t in ("booking_approved", "booking_cancelled"):
            filtered.append(n)
            continue

        # — CLUB_EVENT logic —
        if t == "club_event":
            if not want_clubs:
                # user has globally turned off club events
                continue

            # find this notification's ClubID via EVENT_DETAILS
            cur.execute("""
              SELECT ed.ClubID
              FROM NOTIFICATIONS n2
              JOIN EVENT_DETAILS ed ON n2.BookingID = ed.BookingID
              WHERE n2.NotificationID = %s
            """, (n["NotificationID"],))
            row = cur.fetchone()
            club_id = row["ClubID"] if row else None
            if club_id is None:
                continue

            # check per‑club setting
            cur.execute("""
              SELECT WantsThisClubNotifications
              FROM USER_CLUB_PREFS
              WHERE UserID = %s AND ClubID = %s
            """, (user_id, club_id))
            club_pref = cur.fetchone()
            if club_pref and not club_pref["WantsThisClubNotifications"]:
                continue

            filtered.append(n)
            continue

        # — UNIVERSITY_EVENT logic —
        if t == "university_event":
            if not want_unis:
                # user has globally turned off university events
                continue

            # find all topics for this notification's BookingID
            cur.execute("""
              SELECT Topic
              FROM EVENT_TOPICS
              WHERE BookingID = (
                SELECT BookingID FROM NOTIFICATIONS WHERE NotificationID = %s
              )
            """, (n["NotificationID"],))
            topics = [r["Topic"] for r in cur.fetchall()]

            # if ANY topic is still wanted, keep the notification
            keep = False
            for topic in topics:
                cur.execute("""
                  SELECT WantsNotification
                  FROM USER_EVENT_TOPIC_PREFS
                  WHERE UserID = %s AND Topic = %s
                """, (user_id, topic))
                ep = cur.fetchone()
                if ep is None or ep["WantsNotification"]:
                    keep = True
                    break
            if keep:
                filtered.append(n)
            continue

        # — any other types (e.g. points_confirmation) —
        #    you can choose to include or exclude; here we include them:
        filtered.append(n)

    # cleanup
    cur.close()
    conn.close()

    return jsonify(success=True, notifications=filtered), 200


def get_all_student_notifications(cur, user_id):
    cur.execute("""
        SELECT N.NotificationID, N.BookingID, N.Title, N.Message, N.Type
        FROM NOTIFICATIONS N
        JOIN GETS_STUDENT GS ON N.NotificationID = GS.NotificationID
        WHERE GS.StudentID = %s
        ORDER BY N.NotificationID DESC
    """, (user_id,))
    return cur.fetchall()


def get_all_club_notifications(cur, user_id):
    cur.execute("""
        SELECT N.NotificationID, N.BookingID, N.Title, N.Message, N.Type
        FROM NOTIFICATIONS N
        JOIN GETS_CLUB GC ON N.NotificationID = GC.NotificationID
        WHERE GC.ClubID = %s
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
