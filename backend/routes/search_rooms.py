from flask import Blueprint, request, jsonify
from backend.config import get_connection
from datetime import datetime, timedelta

rooms_bp = Blueprint("rooms", __name__)

@rooms_bp.route("/search", methods=["GET"])
def search_rooms():
    # 1) Parse query parameters
    building      = request.args.get("building")           # e.g. "Engineering"
    date          = request.args.get("date")               # YYYY‑MM‑DD
    hour          = request.args.get("hour")               # HH:MM
    duration      = int(request.args.get("duration", 1))   # hours, default 1
    features_q    = request.args.get("features", "")     # comma‑sep list
    capacity_q    = request.args.get("capacity")           # minimum capacity

    # Normalize features and capacity
    features = [f.strip().lower() for f in features_q.split(",") if f.strip()]
    required_capacity = int(capacity_q) if capacity_q else None

    # Precompute requested start/end times (as HH:MM:SS strings)
    requested_start = requested_end = None
    if date and hour:
        # ensure seconds and compute end
        requested_start = datetime.strptime(hour, "%H:%M").time().strftime("%H:%M:%S")
        dt0 = datetime.strptime(f"{date} {requested_start}", "%Y-%m-%d %H:%M:%S")
        requested_end = (dt0 + timedelta(hours=duration)).time().strftime("%H:%M:%S")

    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)

        # 2) Build base ROOM query (only building & capacity here)
        sql    = "SELECT RoomNumber, Building, Capacity FROM ROOMS"
        cond   = []
        params = []
        if building:
            cond.append("Building = %s")
            params.append(building)
        if required_capacity is not None:
            cond.append("Capacity >= %s")
            params.append(required_capacity)
        if cond:
            sql += " WHERE " + " AND ".join(cond)

        cursor.execute(sql, params)
        rooms = cursor.fetchall()

        available = []

        # 3) For each room, check availability and features
        for room in rooms:
            rn = room["RoomNumber"]
            bd = room["Building"]

            # 3a) Time-slot overlap check
            if date and hour:
                overlap_sql = """
                    SELECT 1
                      FROM TIME_SLOT t
                     WHERE t.RoomNumber = %s
                       AND t.Building   = %s
                       AND t.Date       = %s
                       AND t.Hour < ADDTIME(%s, SEC_TO_TIME(%s*3600))
                       AND ADDTIME(t.Hour, SEC_TO_TIME(t.Duration*3600)) > %s
                """
                cursor.execute(overlap_sql, (
                    rn, bd, date,
                    requested_end, duration,
                    requested_start
                ))
                if cursor.fetchone():
                    continue  # busy

            elif date:
                # existing full-day logic (if needed)
                day_start = datetime.strptime("06:00:00", "%H:%M:%S")
                day_end   = datetime.strptime("22:00:00", "%H:%M:%S")
                cursor.execute(
                    """
                    SELECT Hour, Duration FROM TIME_SLOT
                     WHERE RoomNumber = %s
                       AND Building   = %s
                       AND Date       = %s
                    """, (rn, bd, date)
                )
                bookings = cursor.fetchall()
                booked_start = booked_end = None
                for bk in bookings:
                    bs = datetime.strptime(str(bk["Hour"]), "%H:%M:%S")
                    be = bs + timedelta(hours=bk["Duration"])
                    if booked_start is None or bs < booked_start:
                        booked_start = bs
                    if booked_end is None or be > booked_end:
                        booked_end = be
                if booked_start and booked_end:
                    if booked_start <= day_start and booked_end >= day_end:
                        continue  # fully booked

            # 3b) Feature check
            if features:
                cursor.execute(
                    "SELECT Feature_Name FROM FEATURES WHERE RoomNumber = %s AND Building = %s",
                    (rn, bd)
                )
                room_feats = {r["Feature_Name"].lower() for r in cursor.fetchall()}
                if not all(f in room_feats for f in features):
                    continue

            # 3c) Passed all filters — collect info
            cursor.execute(
                "SELECT Feature_Name FROM FEATURES WHERE RoomNumber = %s AND Building = %s",
                (rn, bd)
            )
            feats_list = [r["Feature_Name"] for r in cursor.fetchall()]

            available.append({
                "roomNumber": rn,
                "building":   bd,
                "capacity":   room.get("Capacity"),
                "features":   feats_list
            })

        cursor.close()
        conn.close()
        return jsonify(available), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rooms_bp.route("/test", methods=["GET"])
def test_rooms():
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
