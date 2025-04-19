from flask import Blueprint, request, jsonify
from backend.config import get_connection

scheduler_bp = Blueprint("scheduler", __name__)


# Function to see if a timeslot is overlapping or not; used in adding and updating timeslot function.
def is_overlapping_reservation(date, hour, duration, room_number, building, exclude_booking_id=None):
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Compute end time of the new timeslot.
        cursor.execute("SELECT ADDTIME(%s, SEC_TO_TIME(%s * 60))", (hour, duration))
        (new_end,) = cursor.fetchone()

        query = """
            SELECT *
            FROM TIME_SLOT
            WHERE RoomNumber = %s AND Building = %s AND Date = %s
            AND (%s < ADDTIME(Hour, SEC_TO_TIME(Duration * 60)) 
                 AND %s > Hour)
        """
        params = [room_number, building, date, hour, new_end]

        # Exclude the current booking if updating.
        if exclude_booking_id is not None:
            query += " AND BookingID != %s"
            params.append(exclude_booking_id)

        cursor.execute(query, tuple(params))
        overlapping = cursor.fetchall()

        cursor.close()
        connection.close()

        return len(overlapping) > 0

    except Exception as e:
        print(f"Error checking overlapping reservation: {e}")
        return True


# Add a new timeslot.
@scheduler_bp.route("/api/timeslot/add", methods=["POST"])
def add_timeslot():
    try:
        data = request.get_json()
        user_id = data.get('UserID')
        date = data.get('Date')
        hour = data.get('Hour')
        duration = data.get('Duration', 1)
        room_number = data.get('RoomNumber')
        building = data.get('Building')
        booking_type = data.get('BookingType')  
        course_id = data.get('CourseID')
        is_approved = data.get('IsApproved', False)

        if not user_id or not date or not hour or not room_number or not building or not booking_type:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Checking for overlap.
        if is_overlapping_reservation(date, hour, duration, room_number, building):
            return jsonify({"success": False, "message": "This timeslot overlaps with an existing reservation."}), 409

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, date, hour, duration, room_number, building, booking_type, course_id, is_approved))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Timeslot added successfully."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Update timeslot.
@scheduler_bp.route("/api/timeslot/update", methods=["PUT"])
def update_timeslot():
    try:
        data = request.get_json()
        booking_id = data.get('BookingID')
        date = data.get('Date')
        hour = data.get('Hour')
        duration = data.get('Duration', 1)
        room_number = data.get('RoomNumber')
        building = data.get('Building')
        booking_type = data.get('BookingType')
        course_id = data.get('CourseID')
        is_approved = data.get('IsApproved', False)

        if not booking_id or not date or not hour or not room_number or not building or not booking_type:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        # Checking for overlap.
        if is_overlapping_reservation(date, hour, duration, room_number, building, exclude_booking_id=booking_id):
            return jsonify({"success": False, "message": "This timeslot overlaps with an existing reservation."}), 409

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE TIME_SLOT
            SET Date = %s, Hour = %s, Duration = %s, RoomNumber = %s, Building = %s, 
                BookingType = %s, IsApproved = %s
            WHERE BookingID = %s
        """, (date, hour, duration, room_number, building, booking_type, is_approved, booking_id))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Timeslot updated successfully."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    

# Delete timeslot by student or club.
@scheduler_bp.route("/api/timeslot/delete", methods=["DELETE"])
def delete_timeslot():
    try:
        data = request.get_json()
        booking_id = data.get('BookingID')
        user_id = data.get('UserID')
        club_id = data.get('ClubID')

        if not booking_id:
            return jsonify({"success": False, "message": "BookingID is required."}), 400

        connection = get_connection()
        cursor = connection.cursor()

        if user_id or club_id:
            cursor.execute("""
                DELETE FROM TIME_SLOT
                WHERE BookingID = %s AND (UserID = %s OR ClubID = %s)
            """, (booking_id, user_id, club_id))
        else:
            cursor.execute("""
                DELETE FROM TIME_SLOT
                WHERE BookingID = %s
            """, (booking_id,))

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Timeslot deleted successfully."
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Delete timeslot by admin.
@scheduler_bp.route("/api/timeslot/delete_by_admin", methods=["DELETE"])
def delete_timeslot_by_admin():
    try:
        data = request.get_json()
        booking_id = data.get('BookingID')

        if not booking_id:
            return jsonify({"success": False, "message": "BookingID is required."}), 400

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM TIME_SLOT
            WHERE BookingID = %s
        """, (booking_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "message": "Timeslot deleted by admin."}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Get a room's schedule (list of timeslots) for specified date and time.
@scheduler_bp.route("/api/timeslot/room_schedule", methods=["GET"])
def get_room_schedule():
    try:
        room_number = request.args.get('RoomNumber')
        building = request.args.get('Building')
        date = request.args.get('Date')
        hour = request.args.get('Hour')

        if not room_number or not building or not date or not hour:
            return jsonify({"success": False, "message": "Missing required query parameters."}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Updated query to fit the new timeslot table.
        cursor.execute("""
            SELECT * FROM TIME_SLOT
            WHERE RoomNumber = %s AND Building = %s AND Date = %s AND Hour = %s
        """, (room_number, building, date, hour))

        timeslots = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "timeslots": timeslots}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Get avaialable rooms based on booked timeslots.
@scheduler_bp.route("/api/timeslot/available_rooms", methods=["GET"])
def get_available_rooms():
    try:
        date = request.args.get('Date')         # Format: 'YYYY-MM-DD' [MYSQL default format].
        start_hour = request.args.get('StartHour')  # Format: 'HH:MM:SS'    [MYSQL default format].
        end_hour = request.args.get('EndHour')

        if not date or not start_hour or not end_hour:
            return jsonify({"success": False, "message": "Date, StartHour, and EndHour are required."}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT * 
            FROM ROOMS 
            WHERE (RoomNumber, Building) NOT IN (
                SELECT RoomNumber, Building
                FROM TIME_SLOT
                WHERE Date = %s AND Hour BETWEEN %s AND %s
            );
        """, (date, start_hour, end_hour))

        available_rooms = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"success": True, "available_rooms": available_rooms}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Get student's timeslots.
@scheduler_bp.route("/api/timeslot/student_reservations", methods=["GET"])
def get_student_reservations():
    try:
        user_id = request.args.get('UserID')

        if not user_id:
            return jsonify({"success": False, "message": "UserID is required."}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM TIME_SLOT
            WHERE UserID = %s AND BookingType = 'student'
        """, (user_id,))

        reservations = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "reservations": reservations}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# Get club's timeslots.
@scheduler_bp.route("/api/timeslot/club_reservations", methods=["GET"])
def get_club_reservations():
    try:
        user_id = request.args.get('UserID')

        if not user_id:
            return jsonify({"success": False, "message": "UserID (Club) is required."}), 400

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM TIME_SLOT
            WHERE UserID = %s AND BookingType = 'club'
        """, (user_id,))

        reservations = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({"success": True, "reservations": reservations}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500