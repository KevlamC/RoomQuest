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


@points_bp.route('/api/award-points', methods=['POST', 'GET'])  
def award_points():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        now = datetime.now()

        # Find approved bookings that ended within the last minute and haven't been awarded points
        cursor.execute("""
            SELECT BookingID, UserID, BookingType, Duration
            FROM TIME_SLOT
            WHERE IsApproved = TRUE AND PointsAwarded = FALSE
        """)

        bookings = cursor.fetchall()
        awarded = []

        for booking in bookings:
            booking_id = booking['BookingID']
            user_id = booking['UserID']
            duration = booking['Duration']
            booking_type = booking['BookingType']

            # Get start datetime
            cursor.execute("SELECT Date, Hour FROM TIME_SLOT WHERE BookingID = %s", (booking_id,))
            time_data = cursor.fetchone()
            start_dt = datetime.combine(time_data['Date'], (datetime.min + time_data['Hour']).time())
            end_dt = start_dt + timedelta(hours=duration)

            # Allow a 1-minute window for exact match
            if abs((now - end_dt).total_seconds()) <= 60:
                points = duration * 20

                if booking_type == 'student':
                    cursor.execute("UPDATE STUDENT SET Points = Points + %s WHERE ID = %s", (points, user_id))
                elif booking_type == 'club':
                    cursor.execute("UPDATE CLUB SET Points = Points + %s WHERE ID = %s", (points, user_id))

                cursor.execute("UPDATE TIME_SLOT SET PointsAwarded = TRUE WHERE BookingID = %s", (booking_id,))

                awarded.append({
                    "bookingID": booking_id,
                    "userID": user_id,
                    "points": points,
                    "type": booking_type
                })

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "awarded": awarded})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


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
