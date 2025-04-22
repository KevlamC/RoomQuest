from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import timedelta

admin_bp = Blueprint("admin", __name__)

# Getting all unapproved bookings.
@admin_bp.route("/api/admin/unapproved", methods=["GET"])
def get_unapproved_bookings():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM TIME_SLOT
            WHERE IsApproved = FALSE
        """)
        bookings = cursor.fetchall()

        # Convert timedelta fields to strings
        for b in bookings:
            for key, value in b.items():
                if isinstance(value, timedelta):
                    b[key] = str(value)

        cursor.close()
        conn.close()
        return jsonify(bookings), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Approve a booking (admin updates IsApproved to TRUE).
@admin_bp.route("/api/admin/approve", methods=["POST"])
def approve_booking():
    try:
        booking_id = request.args.get("booking_id")

        if not booking_id:
            return jsonify({"error": "Missing booking_id parameter."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE TIME_SLOT
            SET IsApproved = TRUE
            WHERE BookingID = %s
        """, (booking_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Booking approved successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/api/admin/add-booking', methods=['POST', 'GET'])
def admin_add_booking():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Params
        user_id = int(request.args.get('user_id'))  # Must be admin
        date = request.args.get('date')             # Format: YYYY-MM-DD
        hour = request.args.get('hour')             # Format: HH:MM:SS
        duration = int(request.args.get('duration', 1))
        room = request.args.get('room')
        building = request.args.get('building')
        booking_type = request.args.get('booking_type')  # 'admin' or 'university_event'
        course_name = request.args.get('course_name')     # Optional
        session_id = request.args.get('session_id')       # Optional
        course_type = request.args.get('course_type')     # Optional: 'Lecture', 'Tutorial', 'Lab'

        if booking_type not in ['admin', 'university_event']:
            return jsonify({"message": "Invalid booking type. Admin can only book 'admin' or 'university_event'."}), 400

        course_id = None
        if course_name and session_id and course_type:
            # Insert into COURSE table
            cursor.execute("""
                INSERT INTO COURSE (CourseName, SessionID, Type)
                VALUES (%s, %s, %s)
            """, (course_name, session_id, course_type))
            course_id = cursor.lastrowid

        # Insert into TIME_SLOT
        cursor.execute("""
            INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (user_id, date, hour, duration, room, building, booking_type, course_id))

        booking_id = cursor.lastrowid
        connection.commit()

        booking_info = {
            "BookingID": booking_id,
            "UserID": user_id,
            "Date": date,
            "Hour": hour,
            "Duration": duration,
            "RoomNumber": room,
            "Building": building,
            "BookingType": booking_type,
            "CourseID": course_id,
            "CourseName": course_name,
            "SessionID": session_id,
            "CourseType": course_type,
            "IsApproved": True
        }

        return jsonify({
            "message": "Booking added successfully.",
            "booking_details": booking_info
        }), 200

    except Exception as e:
        connection.rollback()
        return jsonify({
            "message": "Error adding booking",
            "error": str(e)
        }), 500

    finally:
        cursor.close()
        connection.close()

# Delete a reservation/lecture/tutorial/lab (no ownership check needed).
@admin_bp.route('/api/admin/delete-booking', methods=['POST', 'GET'])
def admin_delete_booking():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        user_id = int(request.args.get('user_id'))  # Must be admin
        booking_id = request.args.get('booking_id')
        course_name = request.args.get('course_name')
        session_id = request.args.get('session_id')  # Optional
        course_type = request.args.get('course_type')  # Optional: Lecture, Lab, Tutorial

        # Verify admin
        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        if result is None or result[0] != 'admin':
            return jsonify({"message": "Unauthorized. Only admins can delete bookings."}), 403

        deleted_info = {}

        if booking_id:
            cursor.execute("SELECT * FROM TIME_SLOT WHERE BookingID = %s", (booking_id,))
            booking_data = cursor.fetchone()
            if not booking_data:
                return jsonify({"message": f"No booking found with BookingID {booking_id}."}), 404

            columns = [desc[0] for desc in cursor.description]
            deleted_info["deleted_booking"] = dict(zip(columns, booking_data))

            cursor.execute("DELETE FROM TIME_SLOT WHERE BookingID = %s", (booking_id,))
            connection.commit()

            return jsonify({
                "message": f"Booking {booking_id} deleted successfully.",
                "details": deleted_info
            }), 200

        elif course_name and course_type:
            # Get matching course(s)
            if session_id:
                cursor.execute("""
                    SELECT * FROM COURSE WHERE CourseName = %s AND SessionID = %s AND Type = %s
                """, (course_name, session_id, course_type))
            else:
                cursor.execute("""
                    SELECT * FROM COURSE WHERE CourseName = %s AND Type = %s
                """, (course_name, course_type))

            course_rows = cursor.fetchall()
            if not course_rows:
                return jsonify({"message": "No matching course(s) found."}), 404

            course_columns = [desc[0] for desc in cursor.description]
            deleted_info["deleted_courses"] = [dict(zip(course_columns, row)) for row in course_rows]
            course_ids = [row[0] for row in course_rows]  # CourseID

            # Get related bookings
            format_ids = ','.join(['%s'] * len(course_ids))
            cursor.execute(f"SELECT * FROM TIME_SLOT WHERE CourseID IN ({format_ids})", course_ids)
            timeslot_rows = cursor.fetchall()
            if timeslot_rows:
                timeslot_columns = [desc[0] for desc in cursor.description]
                deleted_info["deleted_bookings"] = [dict(zip(timeslot_columns, row)) for row in timeslot_rows]

            # Delete bookings
            cursor.execute(f"DELETE FROM TIME_SLOT WHERE CourseID IN ({format_ids})", course_ids)
            # Delete courses
            cursor.execute(f"DELETE FROM COURSE WHERE CourseID IN ({format_ids})", course_ids)

            connection.commit()

            return jsonify({
                "message": "Deleted course(s) and all associated bookings.",
                "details": deleted_info
            }), 200

        else:
            return jsonify({"message": "Must provide booking_id or course_name + course_type to delete."}), 400

    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Error during deletion", "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()