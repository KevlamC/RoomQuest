from flask import Blueprint, request, jsonify
from backend.config import get_connection

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

# Add a new schedule (Lecture, Tutorial, Reservation, etc.).
@admin_bp.route("/api/admin/add-schedule", methods=["POST"])
def add_schedule():
    try:
        data = request.get_json()

        user_id      = data.get("user_id")       # Can be null
        course_id    = data.get("course_id")     # Can be null
        date         = data.get("date")
        hour         = data.get("hour")
        duration     = data.get("duration", 1)
        room_number  = data.get("room_number")
        building     = data.get("building")
        booking_type = data.get("booking_type")  # Lecture, Tutorial, etc.

        if not all([date, hour, room_number, building, booking_type]):
            return jsonify({"error": "Missing required fields."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (user_id, date, hour, duration, room_number, building, booking_type, course_id))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Schedule added successfully."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete a reservation/lecture/tutorial (no ownership check needed).
@admin_bp.route("/api/admin/delete-schedule", methods=["DELETE"])
def delete_schedule():
    try:
        booking_id = request.args.get("booking_id")

        if not booking_id:
            return jsonify({"error": "Missing booking_id parameter."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM TIME_SLOT
            WHERE BookingID = %s
        """, (booking_id,))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Booking deleted successfully."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500