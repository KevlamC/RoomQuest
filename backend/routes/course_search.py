from flask import Blueprint, request, jsonify
from backend.config import get_connection
import datetime

course_bp = Blueprint('course', __name__)

def serialize_row(columns, row):
    def serialize_value(val):
        if isinstance(val, (datetime.date, datetime.time, datetime.datetime)):
            return val.isoformat()
        elif isinstance(val, datetime.timedelta):
            return int(val.total_seconds() // 60)  # Convert to minutes
        return val
    return {col: serialize_value(val) for col, val in zip(columns, row)}

@course_bp.route('/api/student/search-course', methods=['GET', 'POST'])
def search_course():
    try:
        course_name = request.args.get('course_name')
        if not course_name:
            return jsonify({"message": "Missing course_name parameter"}), 400

        connection = get_connection()
        cursor = connection.cursor()

        # Get all course sections (Lecture/Tutorial/Lab) for that course name
        cursor.execute("""
            SELECT c.CourseID, c.CourseName, c.SessionID, c.Type,
                   t.BookingID, t.Date, t.Hour, t.Duration,
                   t.RoomNumber, t.Building, t.BookingType,
                   r.Capacity
            FROM COURSE c
            LEFT JOIN TIME_SLOT t ON c.CourseID = t.CourseID
            LEFT JOIN ROOMS r ON t.RoomNumber = r.RoomNumber AND t.Building = r.Building
            WHERE c.CourseName = %s
            ORDER BY c.SessionID
        """, (course_name,))

        rows = cursor.fetchall()
        if not rows:
            return jsonify({"message": f"No sessions found for course '{course_name}'"}), 404

        columns = [desc[0] for desc in cursor.description]
        result = [serialize_row(columns, row) for row in rows]

        return jsonify({
            "message": f"Found {len(result)} session(s) for {course_name}",
            "sessions": result
        }), 200

    except Exception as e:
        return jsonify({"message": "Error retrieving course info", "error": str(e)}), 500