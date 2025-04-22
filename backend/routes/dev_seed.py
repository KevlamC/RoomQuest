# from flask import Blueprint, jsonify
# from backend.config import get_connection

# dev_bp = Blueprint('dev_seed', __name__)

# @dev_bp.route('/myseed', methods=['GET'])
# def seed_test_data():
#     try:
#         connection = get_connection()
#         cursor = connection.cursor(dictionary=True)

#         # Insert test users
#         users = [
#             (1, "student1@example.com", "student1", "pass123", "student"),
#             (2, "student2@example.com", "student2", "pass123", "student"),
#             (3, "student3@example.com", "student3", "pass123", "student"),
#             (4, "club1@example.com", "clubOne", "clubpass", "club"),
#             (5, "club2@example.com", "clubTwo", "clubpass", "club"),
#             (987654321, "admin@university.edu", "admin1", "adminpass123", "admin")
#         ]
#         cursor.executemany(
#             "INSERT INTO USER (ID, Email, Username, Password, userType) VALUES (%s, %s, %s, %s, %s)",
#             users
#         )

#         # Insert clubs
#         clubs = [
#             (4, 100),
#             (5, 100)
#         ]
#         cursor.executemany("INSERT INTO CLUB (ID, Points) VALUES (%s, %s)", clubs)

#         # Insert time slots
#         timeslots = [
#             (101, 4, "2025-05-01", "10:00:00", 4, "101", "Engineering", "club_event", None, True, True),
#             (102, 987654321, "2025-05-02", "13:00:00", 2, "201", "Science", "university_event", None, True, True),
#             (103, 5, "2025-05-03", "14:00:00", 3, "303", "Health Center", "club_event", None, True, True),
#             (104, 4, "2025-05-04", "11:00:00", 3, "100", "Business", "club_event", None, True, True),
#             (105, 987654321, "2025-05-05", "09:00:00", 2, "200", "Community Hall", "university_event", None, True, True)
#         ]
#         cursor.executemany(
#             """INSERT INTO TIME_SLOT 
#             (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved, PointsAwarded)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
#             timeslots
#         )

#         # Insert event details
#         events = [
#             (101, "Hackathon", "Annual student hackathon", True, "https://hackathon.com", "club", 4),
#             (102, "AI Conference", "Talks on AI", True, "https://ai.com", "university", None),
#             (103, "Mental Health", "Well-being workshop", True, "", "club", 5),
#             (104, "Startup Pitch", "Entrepreneurship night", True, "https://startup.com", "club", 4),
#             (105, "Green Day", "Sustainability event", True, "", "university", None)
#         ]
#         cursor.executemany(
#             """INSERT INTO EVENT_DETAILS 
#             (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
#             VALUES (%s, %s, %s, %s, %s, %s, %s)""",
#             events
#         )

#         # Insert event topics
#         topics = [
#             (101, "Hackathon"),
#             (102, "Artificial Intelligence"),
#             (103, "Mental Health"),
#             (104, "Entrepreneurship"),
#             (105, "Sustainability")
#         ]
#         cursor.executemany(
#             "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
#             topics
#         )

#         connection.commit()
#         return jsonify({"message": "Test data seeded successfully"})
    
#     except Exception as e:
#         connection.rollback()
#         return jsonify({"message": "Error seeding test data", "error": str(e)}), 500
#     finally:
#         cursor.close()
#         connection.close()