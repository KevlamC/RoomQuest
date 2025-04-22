from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime, timedelta

points_bp = Blueprint('points', __name__)

# 🔹 Get student points
@points_bp.route('/api/student/points', methods=['GET'])
def get_student_points():
    try:
        user_id = request.args.get("userID")
        email = request.args.get("email")

        if not user_id and not email:
            return jsonify({"success": False, "error": "Must provide userID or email"}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if not user_id:
            cursor.execute("SELECT ID FROM USER WHERE Email = %s AND userType = 'student'", (email,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"success": False, "error": "Student not found"}), 404
            user_id = result["ID"]

        cursor.execute("SELECT Points FROM STUDENT WHERE ID = %s", (user_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return jsonify({"success": True, "points": result["Points"]})
        else:
            return jsonify({"success": False, "error": "Student not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@points_bp.route("/api/points/award-points/student", methods=["GET", "POST"])
def award_student_points():
    debug_log = []

    try:
        debug_log.append("Route called: /api/points/award-points/student")

        user_id = request.args.get("UserID")
        debug_log.append(f"Received UserID: {user_id}")

        if not user_id:
            debug_log.append("Missing UserID parameter.")
            return jsonify({
                "success": False,
                "message": "Missing UserID parameter",
                "log": debug_log
            }), 400

        conn = get_connection()
        debug_log.append("Database connection established.")
        cur = conn.cursor(dictionary=True)
        debug_log.append("Database cursor created.")

        # 1) Grab all approved, un‑awarded student bookings for this user
        debug_log.append("Querying TIME_SLOT for approved & unawarded bookings…")
        cur.execute("""
            SELECT 
                BookingID,
                UserID,
                Date,
                Hour,
                Duration
            FROM TIME_SLOT
            WHERE BookingType = 'student'
              AND IsApproved = TRUE
              AND PointsAwarded = FALSE
              AND UserID = %s
        """, (user_id,))
        rows = cur.fetchall()
        debug_log.append(f"MySQL rows fetched: {rows}")

        now = datetime.now()  # your server's local time (America/Edmonton)
        debug_log.append(f"Current server time: {now}")

        total_points = 0
        to_award = []

        for r in rows:
            # build the booking start & end datetimes
            start_dt = datetime.combine(r["Date"], (datetime.min + r["Hour"]).time())
            end_dt   = start_dt + timedelta(hours=r["Duration"])
            debug_log.append(
                f"BookingID {r['BookingID']} → start {start_dt}, end {end_dt}"
            )

            if now >= end_dt:
                debug_log.append(f"  → Eligible (now ≥ end)")
                to_award.append(r)
            else:
                debug_log.append(f"  → **Not** yet ended (now < end)")

        # 2) Award points only for the truly‑ended bookings
        for r in to_award:
            pts = r["Duration"] * 20
            total_points += pts
            debug_log.append(f"Awarding {pts} points for BookingID {r['BookingID']}")
            cur.execute(
                "UPDATE TIME_SLOT SET PointsAwarded = TRUE WHERE BookingID = %s",
                (r["BookingID"],)
            )

        if total_points > 0:
            debug_log.append(f"Updating STUDENT points: +{total_points} for UserID {user_id}")
            cur.execute(
                "UPDATE STUDENT SET Points = Points + %s WHERE ID = %s",
                (total_points, user_id)
            )
        else:
            debug_log.append("No points to award after Python time check.")

        conn.commit()
        cur.close()
        conn.close()
        debug_log.append("Database committed & connection closed.")

        return jsonify({
            "success": True,
            "awarded_points": total_points,
            "message": f"Points awarded for {len(to_award)} past reservations.",
            "log": debug_log
        }), 200

    except Exception as e:
        debug_log.append(f"Exception: {e}")
        return jsonify({
            "success": False,
            "message": str(e),
            "log": debug_log
        }), 500

# 🔹 Get club points
@points_bp.route('/api/club/points', methods=['GET'])
def get_club_points():
    try:
        user_id = request.args.get("userID")
        email = request.args.get("email")

        if not user_id and not email:
            return jsonify({"success": False, "error": "Must provide userID or email"}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if not user_id:
            cursor.execute("SELECT ID FROM USER WHERE Email = %s AND userType = 'club'", (email,))
            result = cursor.fetchone()
            if not result:
                return jsonify({"success": False, "error": "Club not found"}), 404
            user_id = result["ID"]

        cursor.execute("SELECT Points FROM CLUB WHERE ID = %s", (user_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result:
            return jsonify({"success": True, "points": result["Points"]})
        else:
            return jsonify({"success": False, "error": "Club not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@points_bp.route("/api/points/leaderboard", methods=["GET", "POST"])
def rank_students_by_points():
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Join USER and STUDENT tables for names + points
        cur.execute("""
            SELECT u.ID, u.Username, s.Points
            FROM STUDENT s
            JOIN USER u ON s.ID = u.ID
            ORDER BY s.Points DESC
        """)
        rankings = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "rankings": rankings
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
