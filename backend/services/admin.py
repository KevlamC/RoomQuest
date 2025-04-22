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
            return jsonify({"message": "Invalid booking type. Admin can only book admin or university_event."}), 400

        course_id = None
        if course_name and session_id and course_type:
            # Insert into COURSE table
            cursor.execute("""
                INSERT INTO COURSE (CourseName, SessionID, Type)
                VALUES (%s, %s, %s)
            """, (course_name, session_id, course_type))
            course_id = cursor.lastrowid

        # Insert TIME_SLOT
        cursor.execute("""
            INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (user_id, date, hour, duration, room, building, booking_type, course_id))

        connection.commit()
        return jsonify({"message": "Booking added successfully"}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Error adding booking", "error": str(e)}), 500

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

        # Verify admin by checking the userType in USER table
        cursor.execute("SELECT userType FROM USER WHERE ID = %s", (user_id,))
        result = cursor.fetchone()
        
        if result is None or result[0] != 'admin':
            return jsonify({"message": "Unauthorized. Only admins can delete bookings."}), 403

        if booking_id:
            # Delete single booking
            cursor.execute("DELETE FROM TIME_SLOT WHERE BookingID = %s", (booking_id,))
            connection.commit()
            return jsonify({"message": f"Booking {booking_id} deleted successfully."}), 200

        elif course_name and course_type:
            if session_id:
                # Delete specific session of the course
                cursor.execute("""
                    SELECT CourseID FROM COURSE
                    WHERE CourseName = %s AND SessionID = %s AND Type = %s
                """, (course_name, session_id, course_type))
            else:
                # Delete all sessions of this course and type
                cursor.execute("""
                    SELECT CourseID FROM COURSE
                    WHERE CourseName = %s AND Type = %s
                """, (course_name, course_type))

            course_ids = [row[0] for row in cursor.fetchall()]
            if not course_ids:
                return jsonify({"message": "No matching course(s) found."}), 404

            # Delete TIME_SLOTs (will cascade delete related EVENT_DETAILS, NOTIFICATIONS, etc.)
            format_ids = ','.join(['%s'] * len(course_ids))
            cursor.execute(f"DELETE FROM TIME_SLOT WHERE CourseID IN ({format_ids})", course_ids)

            # Delete course records
            cursor.execute(f"DELETE FROM COURSE WHERE CourseID IN ({format_ids})", course_ids)

            connection.commit()
            return jsonify({"message": f"Deleted course(s) and all associated bookings.", "deleted_course_ids": course_ids}), 200

        else:
            return jsonify({"message": "Must provide booking_id or course_name + course_type to delete."}), 400

    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Error during deletion", "error": str(e)}), 500

    finally:
        cursor.close()
        connection.close()