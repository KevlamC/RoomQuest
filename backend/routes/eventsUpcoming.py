from flask import Blueprint, jsonify
from backend.config import get_connection

eventsUpcoming = Blueprint("eventsUpcoming", __name__)

@eventsUpcoming.route("/api/events/upcoming", methods=["GET"])
def get_upcoming_events():
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ed.EventName AS eventTitle,
                   u.Username AS host,
                   ts.Date,
                   ts.Hour AS time,
                   ed.Description AS description
            FROM EVENT_DETAILS ed
            JOIN TIME_SLOT ts ON ed.BookingID = ts.BookingID
            JOIN USER u ON ts.UserID = u.ID
            WHERE ed.IsPublic = TRUE
              AND ts.Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 10 DAY)
            ORDER BY ts.Date ASC, ts.Hour ASC
            LIMIT 10;
        """)

        events = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(events), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

