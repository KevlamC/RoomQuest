from flask import Blueprint, request, jsonify
from backend.config import get_connection

scheduler_bp = Blueprint("scheduler", __name__)

# Add a new timeslot.
@scheduler_bp.route("/api/timeslot/add", methods=["POST"])
def add_timeslot():
    try:
        data = request.get_json()
        user_id = data.get("UserID")
        admin_id = data.get("AdminID")
        club_id = data.get("ClubID")
        date = data.get("Date")
        hour = data.get("Hour")
        duration = data.get("Duration")
        room_id = data.get("RoomID")
        booking_type = data.get("BookingType")

        if not date or not hour or not room_id or not booking_type:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO TIME_SLOT 
            (UserID, AdminID, ClubID, Date, Hour, Duration, RoomID, BookingType)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, admin_id, club_id, date, hour, duration, room_id, booking_type))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Timeslot added successfully."}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Update timeslot.
@scheduler_bp.route("/api/timeslot/update", methods=["PUT"])
def update_timeslot():
    try:
        data = request.get_json()
        booking_id = data.get("BookingID")
        date = data.get("Date")
        hour = data.get("Hour")
        duration = data.get("Duration")
        room_id = data.get("RoomID")
        booking_type = data.get("BookingType")
        admin_id = data.get("AdminID")
        user_id = data.get("UserID")
        club_id = data.get("ClubID")

        if not booking_id or not date or not hour or not booking_type:
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        conn = get_connection()
        cursor = conn.cursor()

        query = """
            UPDATE TIME_SLOT
            SET Date = %s, Hour = %s, Duration = %s, RoomID = %s, BookingType = %s
            WHERE BookingID = %s AND (AdminID = %s OR UserID = %s OR ClubID = %s)
        """
        cursor.execute(query, (date, hour, duration, room_id, booking_type, booking_id, admin_id, user_id, club_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Timeslot updated successfully."}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



