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
    debug_log = []  # For collecting logs

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

        query = """
            SELECT * FROM TIME_SLOT 
            WHERE (BookingType = 'student')
            AND IsApproved = TRUE
            AND PointsAwarded = FALSE
            AND UserID = %s
            AND NOT (
                Date > CURDATE()
                OR
                (
                    Date = CURDATE() 
                    AND ADDTIME(Hour, SEC_TO_TIME(Duration * 3600)) >= CURTIME()
                )
            )
        """
        debug_log.append("Executing query to fetch eligible reservations...")
        cur.execute(query, (user_id,))
        reservations = cur.fetchall()

        debug_log.append(f"Reservations found: {len(reservations)}")
        debug_log.append(f"Reservations detail: {reservations}")

        total_points = 0
        for res in reservations:
            booking_id = res["BookingID"]
            duration_hours = res["Duration"]
            earned_points = duration_hours * 20
            total_points += earned_points

            debug_log.append(f"Awarding {earned_points} points for BookingID {booking_id}")
            cur.execute("UPDATE TIME_SLOT SET PointsAwarded = TRUE WHERE BookingID = %s", (booking_id,))

        if total_points > 0:
            debug_log.append(f"Updating STUDENT points: +{total_points} for UserID {user_id}")
            cur.execute("UPDATE STUDENT SET Points = Points + %s WHERE ID = %s", (total_points, user_id))
        else:
            debug_log.append("No points to award.")

        conn.commit()
        cur.close()
        conn.close()
        debug_log.append("Database changes committed and connection closed.")

        return jsonify({
            "success": True,
            "awarded_points": total_points,
            "message": f"Points awarded for {len(reservations)} past reservations.",
            "log": debug_log
        }), 200

    except Exception as e:
        debug_log.append(f"Exception occurred: {str(e)}")
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
