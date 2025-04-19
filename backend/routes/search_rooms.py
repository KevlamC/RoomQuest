from flask import Blueprint, request, jsonify
from backend.config import get_connection

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/search", methods=["GET"])
def search_rooms():
    # 1) Parse query parameters
    building      = request.args.get("building")           # e.g. "Engineering"
    date          = request.args.get("date")               # YYYY‑MM‑DD
    hour          = request.args.get("hour")               # HH:MM
    duration      = int(request.args.get("duration", 1))   # hours, default 1
    features_q    = request.args.get("features", "")       # comma‑sep list

    # Normalize features into a Python list of lowercase names
    features = [f.strip().lower() for f in features_q.split(",") if f.strip()]

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 2) Build base ROOM query with building filters
        sql  = "SELECT RoomNumber, Building, Capacity FROM ROOMS"
        cond = []
        params = []

        if building:
            cond.append("Building = %s")
            params.append(building)

        if cond:
            sql += " WHERE " + " AND ".join(cond)

        cursor.execute(sql, params)
        rooms = cursor.fetchall()

        available = []

        # 3) For each candidate room, test availability and feature‑matching
        for room in rooms:
            rn = room["RoomNumber"]
            bd = room["Building"]

            # 3a) Availability: ensure no overlapping booking at (date, hour, duration)
            if date and hour:
                # Check for overlapping time slots on the given date
                overlap_sql = """
                    SELECT 1 FROM TIME_SLOT
                    WHERE RoomNumber = %s
                      AND Building   = %s
                      AND Date       = %s
                      AND NOT (
                        ADDTIME(Hour, SEC_TO_TIME(Duration*3600)) <= %s
                        OR Hour >= ADDTIME(%s, SEC_TO_TIME(%s*3600))
                      )
                """
                cursor.execute(overlap_sql, (rn, bd, date, hour, hour, duration))
                if cursor.fetchone():
                    continue  # room is busy at the requested time
            
            elif date:
                # Define the full day range
                day_start = '06:00'  # Start of the day (6 AM)
                day_end = '22:00'    # End of the day (10 PM)
            
                # SQL query to find bookings for this room and date
                date_conflict_sql = """
                    SELECT Hour, Duration FROM TIME_SLOT
                    WHERE RoomNumber = %s
                      AND Building   = %s
                      AND Date       = %s
                """
                cursor.execute(date_conflict_sql, (rn, bd, date))
                bookings = cursor.fetchall()
            
                # Check if bookings overlap the entire day (6 AM to 10 PM)
                booked_start = None
                booked_end = None
            
                for booking in bookings:
                    booking_start = booking["Hour"]
                    booking_end = ADDTIME(booking_start, SEC_TO_TIME(booking["Duration"] * 3600))
            
                    # If this is the first booking, initialize the start and end times
                    if booked_start is None or booking_start < booked_start:
                        booked_start = booking_start
                    if booked_end is None or booking_end > booked_end:
                        booked_end = booking_end
            
                # Now check if the bookings cover the entire day range
                if booked_start <= day_start and booked_end >= day_end:
                    continue  # Skip this room, it's fully booked for the entire day


            # 3b) Feature check: room must have *all* requested features
            if features:
                cursor.execute(
                    "SELECT Feature_Name FROM FEATURES WHERE RoomNumber = %s AND Building = %s",
                    (rn, bd)
                )
                room_feats = {r["Feature_Name"].lower() for r in cursor.fetchall()}
                
                # Check for capacity feature
                capacity_requested = [f for f in features if f.startswith("capacity:")]
                if capacity_requested:
                    required_capacity = int(capacity_requested[0].split(":")[1])  # Extract the required capacity
                    if room["Capacity"] < required_capacity:
                        continue  # Skip if the room capacity is less than required
                
                # Check for other features
                if not all(f in room_feats for f in features):
                    continue

            # 3c) Passed all filters — include full info + its features
            cursor.execute(
                "SELECT Feature_Name FROM FEATURES WHERE RoomNumber = %s AND Building = %s",
                (rn, bd)
            )
            feats_list = [r["Feature_Name"] for r in cursor.fetchall()]

            available.append({
                "roomNumber": rn,
                "building": bd,
                "capacity": room.get("Capacity"),
                "features": feats_list
            })

        cursor.close()
        conn.close()
        return jsonify(available), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rooms_bp.route("/test", methods=["GET"])
def test_rooms():
    """Simple endpoint: returns all rooms (no filters)."""
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ROOMS")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
