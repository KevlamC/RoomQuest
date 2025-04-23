from flask import Blueprint, jsonify
from backend.config import get_connection

# MY SEED FOR SEARCH EVENTS 

dev_bp = Blueprint('dev_seed', __name__)

@dev_bp.route('/myseed', methods=['GET'])
def seed_test_data():
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        # Clean up old data
        cursor.execute("DELETE FROM USER;")
        cursor.execute("DELETE FROM TIME_SLOT;")
        cursor.execute("DELETE FROM CLUB;")
        cursor.execute("DELETE FROM EVENT_DETAILS;")
        cursor.execute("DELETE FROM EVENT_TOPICS;")

        # Insert test users
        users = [
            (1, "student1@example.com", "student1", "pass123", "student"),
            (2, "student2@example.com", "student2", "pass123", "student"),
            (3, "student3@example.com", "student3", "pass123", "student"),
            (4, "club1@example.com", "clubOne", "clubpass", "club"),
            (5, "club2@example.com", "clubTwo", "clubpass", "club"),
            (987654321, "admin@example.com", "admin1", "adminpass", "admin")
        ]
        cursor.executemany(
            "INSERT INTO USER (ID, Email, Username, Password, userType) VALUES (%s, %s, %s, %s, %s)",
            users
        )

        # Insert clubs
        clubs = [
            (4, 100),
            (5, 100)
        ]
        cursor.executemany("INSERT INTO CLUB (ID, Points) VALUES (%s, %s)", clubs)

        # Insert rooms (must exist before TIME_SLOT due to FK constraints)
        rooms = [
            ("101", "Engineering", 50),
            ("201", "Science", 100),
            ("303", "Health Center", 30),
            ("100", "Business", 40),
            ("200", "Community Hall", 200)
        ]
        cursor.executemany(
            "INSERT INTO ROOMS (RoomNumber, Building, Capacity) VALUES (%s, %s, %s)",
            rooms
        )

        # Insert base time slots
        timeslots = [
            (101, 4, "2025-05-01", "10:00:00", 4, "101", "Engineering", "club_event", None, True, True),
            (102, 987654321, "2025-05-02", "13:00:00", 2, "201", "Science", "university_event", None, True, True),
            (103, 5, "2025-05-03", "14:00:00", 3, "303", "Health Center", "club_event", None, True, True),
            (104, 4, "2025-05-04", "11:00:00", 3, "100", "Business", "club_event", None, True, True),
            (105, 987654321, "2025-05-05", "09:00:00", 2, "200", "Community Hall", "university_event", None, True, True)
        ]
        cursor.executemany(
            """INSERT INTO TIME_SLOT 
            (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved, PointsAwarded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            timeslots
        )

        # Insert base event details
        events = [
            (101, "Hackathon", "Annual student hackathon", True, "https://hackathon.com", "club", 4),
            (102, "AI Conference", "Talks on AI", True, "https://ai.com", "university", None),
            (103, "Mental Health", "Well-being workshop", True, "", "club", 5),
            (104, "Startup Pitch", "Entrepreneurship night", True, "https://startup.com", "club", 4),
            (105, "Green Day", "Sustainability event", True, "", "university", None)
        ]
        cursor.executemany(
            """INSERT INTO EVENT_DETAILS 
            (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            events
        )

        # Insert base event topics
        topics = [
            (101, "Hackathon"),
            (102, "Artificial Intelligence"),
            (103, "Mental Health"),
            (104, "Entrepreneurship"),
            (105, "Sustainability")
        ]
        cursor.executemany(
            "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
            topics
        )

        # EXTRA 15 BOOKINGS

        # 15 new time slots
        extra_timeslots = [
            (106, 1, "2025-05-06", "10:00:00", 2, "101", "Engineering", "student", None, False, True),
            (107, 1, "2025-05-07", "11:00:00", 1, "201", "Science", "student", None, True, True),
            (108, 1, "2025-05-08", "09:00:00", 2, "303", "Health Center", "student", None, True, True),
            (109, 1, "2025-05-09", "12:00:00", 1, "100", "Business", "student", None, False, False),
            (110, 1, "2025-05-10", "13:00:00", 2, "200", "Community Hall", "student", None, True, True),
            (111, 5, "2025-05-11", "14:00:00", 2, "101", "Engineering", "club_event", None, False, True),
            (112, 5, "2025-05-12", "15:00:00", 2, "201", "Science", "club_event", None, True, True),
            (113, 5, "2025-05-13", "10:00:00", 1, "303", "Health Center", "club_event", None, True, True),
            (114, 5, "2025-05-14", "11:00:00", 1, "100", "Business", "club_event", None, False, False),
            (115, 5, "2025-05-15", "09:00:00", 2, "200", "Community Hall", "club_event", None, True, True),
            (116, 987654321, "2025-05-16", "10:00:00", 2, "101", "Engineering", "university_event", None, False, False),
            (117, 2, "2025-05-17", "13:00:00", 2, "201", "Science", "student", None, False, True),
            (118, 3, "2025-05-18", "09:00:00", 2, "303", "Health Center", "student", None, False, True),
            (119, 987654321, "2025-05-19", "12:00:00", 1, "100", "Business", "university_event", None, False, True),
            (120, 2, "2025-05-20", "13:00:00", 2, "200", "Community Hall", "student", None, False, True)
        ]
        cursor.executemany("""
            INSERT INTO TIME_SLOT 
            (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, extra_timeslots)

        # Matching event details
        extra_events = [
            (106, "Career Fair", "Meet industry reps", True, "", "university", None),
            (107, "Resume Workshop", "Improve your resume", True, "", "university", None),
            (108, "Exam Prep", "Final exam help session", True, "", "club", 5),
            (109, "Student Meetup", "Make new friends", True, "", "university", None),
            (110, "Chess Tournament", "Chess battles!", True, "", "university", None),
            (111, "Tech Showcase", "Cool club inventions", True, "", "club", 5),
            (112, "Robotics Demo", "Robot competition", True, "", "club", 5),
            (113, "Gaming Night", "Board and video games", True, "", "club", 5),
            (114, "Art Expo", "Art from our members", True, "", "club", 5),
            (115, "Dance Workshop", "Club-led dance class", True, "", "club", 5),
            (116, "Open House", "Campus-wide event", True, "", "university", None),
            (117, "Workshop: Study Skills", "Tips for academic success", True, "", "university", None),
            (118, "Mental Wellness", "De-stress tips", True, "", "university", None),
            (119, "Alumni Talk", "Hear from grads", True, "", "university", None),
            (120, "Coding Bootcamp", "Learn to code fast", True, "", "university", None)
        ]
        cursor.executemany("""
            INSERT INTO EVENT_DETAILS 
            (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, extra_events)

        # Matching event topics
        extra_topics = [
            (106, "Career Development"),
            (107, "Resumes"),
            (108, "Study Help"),
            (109, "Community"),
            (110, "Board Games"),
            (111, "Technology"),
            (112, "Robotics"),
            (113, "Gaming"),
            (114, "Art"),
            (115, "Dance"),
            (116, "Campus Life"),
            (117, "Study Skills"),
            (118, "Mental Health"),
            (119, "Alumni"),
            (120, "Programming")
        ]
        cursor.executemany(
            "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
            extra_topics
        )

        connection.commit()
        return jsonify({"message": "Test data seeded successfully"})
    
    except Exception as e:
        connection.rollback()
        return jsonify({"message": "Error seeding test data", "error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()