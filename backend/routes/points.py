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


@points_bp.route("/api/points/award-points", methods=["GET", "POST"])
def award_student_points():
    try:
        user_id = request.args.get("UserID")
        if not user_id:
            return jsonify({"success": False, "message": "Missing UserID parameter"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Fetch eligible past reservations that haven't been awarded points yet
        cur.execute("""
            SELECT * FROM TIME_SLOT 
            WHERE (BookingType = 'student' OR BookingType = 'club')
              AND ((ADDTIME(Hour, SEC_TO_TIME(Duration*3600)) <= CURTIME()) AND (Date <= CURDATE()))
              AND IsApproved = TRUE AND PointsAwarded = FALSE AND UserID = %s
        """, (user_id,))
        reservations = cur.fetchall()

        total_points = 0
        for res in reservations:
            booking_id = res["BookingID"]
            duration_hours = res["Duration"]
            earned_points = duration_hours * 20
            total_points += earned_points

            # Update PointsAwarded to TRUE
            cur.execute("UPDATE TIME_SLOT SET PointsAwarded = TRUE WHERE BookingID = %s", (booking_id,))

            # Insert into POINTS_TRANSACTION
            cur.execute("""
                INSERT INTO POINTS_TRANSACTION (TransactionID, StudentID, PointsChange, TransactionDate, Description)
                VALUES (UUID_SHORT(), %s, %s, NOW(), %s)
            """, (user_id, earned_points, f"Points for past reservation ID {booking_id}"))

        # Update student's points balance
        if total_points > 0:
            cur.execute("UPDATE STUDENT SET Points = Points + %s WHERE ID = %s", (total_points, user_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "awarded_points": total_points,
            "message": f"Points awarded for {len(reservations)} past reservations."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


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
