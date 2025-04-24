from flask import Blueprint, request, jsonify
from backend.config import get_connection
import datetime

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
        rows = cursor.fetchall()

        # Serialize to avoid JSON issues
        def serialize_row(row):
            for key, value in row.items():
                if isinstance(value, datetime.timedelta):
                    row[key] = int(value.total_seconds() // 3600)
                elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
                    row[key] = str(value)
            return row

        results = [serialize_row(row) for row in rows]

        cursor.close()
        connection.close()
        return jsonify(results)

    except Exception as e:
        return jsonify({"message": "Search failed", "error": str(e)})

@event_search_bp.route('/api/events/add', methods=['POST', 'GET'])
def add_event():
    try:
        # Required Booking Info
        user_id = request.args.get('user_id', type=int)
        date = request.args.get('date')
        hour = request.args.get('time')  # 'time' is used for 'Hour' column
        duration = request.args.get('duration', type=int)
        room_number = request.args.get('room_number')
        building = request.args.get('building')
        booking_type = request.args.get('booking_type')
        
        # Optional course info
        course_name = request.args.get('course_name')
        session_id = request.args.get('session_id')
        course_type = request.args.get('course_type')

        # Required Event Info
        event_name = request.args.get('event_name')

        # Optional Event Info
        description = request.args.get('description')
        is_public = request.args.get('is_public', default=True, type=lambda v: v.lower() == 'true')
        link = request.args.get('link')
        club_id = request.args.get('club_id', type=int)

        if not all([user_id, date, hour, duration, room_number, building, booking_type, event_name]):
            return jsonify({'success': False, 'error': 'Missing required booking/event fields'}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Lookup or insert CourseID if course details provided
        course_id = None
        if course_name and session_id and course_type:
            cursor.execute("""
                SELECT CourseID FROM COURSE
                WHERE CourseName = %s AND SessionID = %s AND Type = %s
            """, (course_name, session_id, course_type))
            course_row = cursor.fetchone()

            if course_row:
                course_id = course_row[0]
            else:
                cursor.execute("""
                    INSERT INTO COURSE (CourseName, SessionID, Type)
                    VALUES (%s, %s, %s)
                """, (course_name, session_id, course_type))
                conn.commit()
                course_id = cursor.lastrowid

        # Insert into TIME_SLOT
        cursor.execute("""
            INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, FALSE)
        """, (user_id, date, hour, duration, room_number, building, booking_type, course_id))
        booking_id = cursor.lastrowid

        # Determine EventType
        if booking_type not in ['club_event', 'university_event']:
            return jsonify({'success': False, 'error': f'Invalid BookingType: {booking_type}'}), 400
        event_type = 'club' if booking_type == 'club_event' else 'university'

        # Insert into EVENT_DETAILS
        cursor.execute("""
            INSERT INTO EVENT_DETAILS (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, event_name, description, is_public, link, event_type, club_id if event_type == 'club' else None))

        conn.commit()
        return jsonify({'success': True, 'message': 'Event and booking added successfully!', 'booking_id': booking_id})

    except Exception as e:
        print("Error in add_event:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
    
@event_search_bp.route('/api/events/delete', methods=['POST', 'GET'])
def delete_event():
    try:
        booking_id = request.args.get('booking_id', type=int)
        if not booking_id:
            return jsonify({'success': False, 'error': 'Missing booking_id'}), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Check if the event exists
        cursor.execute("SELECT * FROM EVENT_DETAILS WHERE BookingID = %s", (booking_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Event not found'}), 404

        # Delete from TIME_SLOT (will cascade delete EVENT_DETAILS)
        cursor.execute("DELETE FROM TIME_SLOT WHERE BookingID = %s", (booking_id,))
        conn.commit()

        return jsonify({'success': True, 'message': f'Event with BookingID {booking_id} deleted successfully.'})

    except Exception as e:
        print("Error in delete_event:", e)
        return jsonify({'success': False, 'error': str(e)}), 500
