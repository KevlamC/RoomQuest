from flask import Blueprint, request, jsonify
from backend.config import get_connection

event_search_bp = Blueprint('event_search', __name__)

@event_search_bp.route('/api/events/search', methods=['GET', 'POST'])
def search_events():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        event_name = request.args.get('event_name')
        club_name = request.args.get('club_name')
        date = request.args.get('date')
        hour = request.args.get('hour')
        building = request.args.get('building')
        room = request.args.get('room')
        topic = request.args.get('topic')

        query = """
        SELECT 
            ED.EventName, ED.Description, ED.Link, ED.EventType,
            U.Username AS ClubName,
            TS.Date, TS.Hour, TS.Duration,
            TS.Building, TS.RoomNumber,
            ET.Topic
        FROM EVENT_DETAILS ED
        JOIN TIME_SLOT TS ON ED.BookingID = TS.BookingID
        LEFT JOIN CLUB C ON ED.ClubID = C.ID
        LEFT JOIN USER U ON C.ID = U.ID
        LEFT JOIN EVENT_TOPICS ET ON ED.BookingID = ET.BookingID
        WHERE ED.IsPublic = TRUE
        """
        filters = []
        values = []

        if event_name:
            filters.append("ED.EventName LIKE %s")
            values.append(f"%{event_name}%")
        if club_name:
            filters.append("U.Username LIKE %s")
            values.append(f"%{club_name}%")
        if date:
            filters.append("TS.Date = %s")
            values.append(date)
        if hour:
            filters.append("TS.Hour = %s")
            values.append(hour)
        if building:
            filters.append("TS.Building = %s")
            values.append(building)
        if room:
            filters.append("TS.RoomNumber = %s")
            values.append(room)
        if topic:
            filters.append("ET.Topic = %s")
            values.append(topic)

        if filters:
            query += " AND " + " AND ".join(filters)

        cursor.execute(query, tuple(values))
        results = cursor.fetchall()

        # Convert Duration if needed
        for row in results:
            if 'Duration' in row and hasattr(row['Duration'], 'total_seconds'):
                row['Duration'] = int(row['Duration'].total_seconds() // 3600)

        cursor.close()
        connection.close()
        return jsonify(results)

    except Exception as e:
        return jsonify({"message": "Search failed", "error": str(e)})
