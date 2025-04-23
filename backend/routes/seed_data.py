from flask import Blueprint, jsonify
from datetime import date, timedelta
from backend.config import get_connection

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed', methods=['GET'])
def run_seeding():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Clear all data first to prevent duplicates
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM GETS_CLUB;")
        cursor.execute("DELETE FROM GETS_STUDENT;")
        cursor.execute("DELETE FROM IS_MEMBER;")
        cursor.execute("DELETE FROM USER_EVENT_TOPIC_PREFS;")
        cursor.execute("DELETE FROM NOTIFICATION_PREFS;")
        cursor.execute("DELETE FROM NOTIFICATIONS;")
        cursor.execute("DELETE FROM EVENT_TOPICS;")
        cursor.execute("DELETE FROM EVENT_DETAILS;")
        cursor.execute("DELETE FROM TIME_SLOT;")
        cursor.execute("DELETE FROM FEATURES;")
        cursor.execute("DELETE FROM ROOMS;")
        cursor.execute("DELETE FROM COURSE;")
        cursor.execute("DELETE FROM STUDENT;")
        cursor.execute("DELETE FROM CLUB;")
        cursor.execute("DELETE FROM ADMIN;")
        cursor.execute("DELETE FROM USER;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Seed all data
        seed_users(cursor)
        seed_rooms_and_features(cursor)
        seed_timeslots(cursor)
        seed_notifications_and_prefs(cursor)
        seed_event_details_and_topics(cursor)
        seed_course_data(cursor)
        
        conn.commit()
        return jsonify({"message": "Database seeded successfully ✅"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

def seed_users(cursor):
    users = [
        # Original users
        {"ID": 1, "Email": "student1@x.com", "Username": "s1", "Password": "p1", "userType": "student"},
        {"ID": 2, "Email": "student2@x.com", "Username": "s2", "Password": "p2", "userType": "student"},
        {"ID": 3, "Email": "student3@x.com", "Username": "s3", "Password": "p3", "userType": "student"},
        {"ID": 4, "Email": "club1@x.com", "Username": "c1", "Password": "p4", "userType": "club"},
        {"ID": 5, "Email": "club2@x.com", "Username": "c2", "Password": "p5", "userType": "club"},
        # Additional users from dev_seed
        {"ID": 987654321, "Email": "admin@example.com", "Username": "admin1", "Password": "adminpass", "userType": "admin"},
        {"ID": 3030, "Email": "tcp@example.com", "Username": "tcp", "Password": "pass123", "userType": "student"},
        {"ID": 80, "Email": "http@example.com", "Username": "http", "Password": "pass123", "userType": "student"},
        {"ID": 6000, "Email": "host@example.com", "Username": "host", "Password": "pass123", "userType": "student"},
        {"ID": 457, "Email": "wics@example.com", "Username": "wics", "Password": "clubpass", "userType": "club"},
        {"ID": 413, "Email": "data@example.com", "Username": "data", "Password": "clubpass", "userType": "club"}
    ]
    
    for u in users:
        cursor.execute(
            "INSERT INTO USER (ID, Email, Username, Password, userType) VALUES (%s, %s, %s, %s, %s)",
            (u["ID"], u["Email"], u["Username"], u["Password"], u["userType"])
        )
        if u["userType"] == "student":
            cursor.execute("INSERT INTO STUDENT (ID, Points) VALUES (%s, 0)", (u["ID"],))
        elif u["userType"] == "club":
            cursor.execute("INSERT INTO CLUB (ID, Points) VALUES (%s, 100)", (u["ID"],))
        elif u["userType"] == "admin":
            cursor.execute("INSERT INTO ADMIN (ID) VALUES (%s)", (u["ID"],))

def seed_rooms_and_features(cursor):
    rooms = [
        # Original rooms
        {"RoomNumber": "101", "Building": "Engineering", "Capacity": 30, "Features": ["whiteboard", "projector", "soundproofing"]},
        {"RoomNumber": "202", "Building": "Science", "Capacity": 25, "Features": ["lab equipment", "computers"]},
        {"RoomNumber": "303", "Building": "Library", "Capacity": 20, "Features": ["whiteboard", "computers"]},
        {"RoomNumber": "404", "Building": "Business", "Capacity": 40, "Features": ["projector", "microphone"]},
        {"RoomNumber": "505", "Building": "Arts", "Capacity": 15, "Features": ["dual projectors", "soundproofing"]},
        {"RoomNumber": "606", "Building": "Medicine", "Capacity": 35, "Features": ["whiteboard", "lab equipment"]},
        {"RoomNumber": "707", "Building": "Law", "Capacity": 50, "Features": ["projector", "recording setup"]},
        {"RoomNumber": "808", "Building": "Fine Arts", "Capacity": 18, "Features": ["soundproofing", "microphone"]},
        {"RoomNumber": "909", "Building": "IT", "Capacity": 28, "Features": ["computers", "projector"]},
        {"RoomNumber": "100A", "Building": "Commerce", "Capacity": 32, "Features": ["whiteboard", "dual projectors", "computers"]},
        # Additional rooms from dev_seed
        {"RoomNumber": "151", "Building": "Engineering", "Capacity": 50, "Features": []},
        {"RoomNumber": "251", "Building": "Science", "Capacity": 100, "Features": []},
        {"RoomNumber": "353", "Building": "Health Center", "Capacity": 30, "Features": []},
        {"RoomNumber": "150", "Building": "Business", "Capacity": 40, "Features": []},
        {"RoomNumber": "230", "Building": "Community Hall", "Capacity": 200, "Features": []}
    ]

    for room in rooms:
        cursor.execute(
            "INSERT INTO ROOMS (RoomNumber, Building, Capacity) VALUES (%s, %s, %s)",
            (room["RoomNumber"], room["Building"], room["Capacity"])
        )
        for feat in room["Features"]:
            cursor.execute(
                "INSERT INTO FEATURES (RoomNumber, Building, Feature_Name) VALUES (%s, %s, %s)",
                (room["RoomNumber"], room["Building"], feat)
            )

def seed_timeslots(cursor):
    # List of timeslot data in exact table column order (excluding auto-incremented BookingID)
    timeslots = [
        # Format: (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
        # Original timeslots
        (1, "2025-04-22", "15:00:00", 3, "101", "Engineering", "student", None, True, True),
        (2, "2025-04-22", "15:00:00", 3, "202", "Science", "student", None, True, False),
        (4, "2025-04-23", "18:00:00", 2, "303", "Library", "club_event", None, True, True),
        (5, "2025-04-24", "19:00:00", 4, "404", "Business", "club_event", None, True, True),
        
        # Additional timeslots from dev_seed
        (4, "2025-05-01", "10:00:00", 4, "101", "Engineering", "club_event", None, True, True),
        (987654321, "2025-05-02", "13:00:00", 2, "201", "Science", "university_event", None, True, True),
        (5, "2025-05-03", "14:00:00", 3, "303", "Health Center", "club_event", None, True, True),
        (4, "2025-05-04", "11:00:00", 3, "100", "Business", "club_event", None, True, True),
        (987654321, "2025-05-05", "09:00:00", 2, "200", "Community Hall", "university_event", None, True, True),
        
        # Extra 15 bookings from dev_seed
        (1, "2025-05-06", "10:00:00", 2, "101", "Engineering", "student", None, True, False),
        (1, "2025-05-07", "11:00:00", 1, "201", "Science", "student", None, True, True),
        (1, "2025-05-08", "09:00:00", 2, "303", "Health Center", "student", None, True, True),
        (1, "2025-05-09", "12:00:00", 1, "100", "Business", "student", None, False, False),
        (1, "2025-05-10", "13:00:00", 2, "200", "Community Hall", "student", None, True, True),
        (5, "2025-05-11", "14:00:00", 2, "101", "Engineering", "club_event", None, True, False),
        (5, "2025-05-12", "15:00:00", 2, "201", "Science", "club_event", None, True, True),
        (5, "2025-05-13", "10:00:00", 1, "303", "Health Center", "club_event", None, True, True),
        (5, "2025-05-14", "11:00:00", 1, "100", "Business", "club_event", None, False, False),
        (5, "2025-05-15", "09:00:00", 2, "200", "Community Hall", "club_event", None, True, True),
        (987654321, "2025-05-16", "10:00:00", 2, "101", "Engineering", "university_event", None, False, False),
        (2, "2025-05-17", "13:00:00", 2, "201", "Science", "student", None, True, False),
        (3, "2025-05-18", "09:00:00", 2, "303", "Health Center", "student", None, True, False),
        (987654321, "2025-05-19", "12:00:00", 1, "100", "Business", "university_event", None, True, False),
        (2, "2025-05-20", "13:00:00", 2, "200", "Community Hall", "student", None, True, False),
        
        # Course-related timeslots
        (987654321, "2025-06-01", "09:00:00", 2, "101", "Engineering", "university_event", 1, True, True),
        (987654321, "2025-06-02", "10:00:00", 1, "101", "Engineering", "university_event", 2, True, True),
        (987654321, "2025-06-03", "11:00:00", 2, "101", "Engineering", "university_event", 3, True, True),
        (987654321, "2025-06-04", "13:00:00", 1, "101", "Engineering", "university_event", 4, True, True)
    ]

    # Insert all timeslots (BookingID will auto-increment)
    cursor.executemany(
        """INSERT INTO TIME_SLOT 
        (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        timeslots
    )

def seed_notifications_and_prefs(cursor):
    # Clean up old data
    cursor.execute("DELETE FROM GETS_STUDENT;")
    cursor.execute("DELETE FROM GETS_CLUB;")
    cursor.execute("DELETE FROM IS_MEMBER;")
    cursor.execute("DELETE FROM NOTIFICATION_PREFS;")
    cursor.execute("DELETE FROM NOTIFICATIONS;")

    # Seed notifications with correct columns
    notifications = [
        {"NotificationID": 1, "BookingID": None, "Title": "Booking Approved", "Message": "Your booking was approved!", "Type": "booking_approved"},
        {"NotificationID": 2, "BookingID": None, "Title": "New Club Event", "Message": "Music Club is hosting a concert.", "Type": "club_event"},
        {"NotificationID": 3, "BookingID": None, "Title": "University Alert", "Message": "Campus will be closed tomorrow.", "Type": "university_event"},
        {"NotificationID": 4, "BookingID": None, "Title": "Points Added", "Message": "You earned 10 points.", "Type": "points_confirmation"},
        # Additional notifications can be added here
    ]
    for n in notifications:
        cursor.execute(
            "INSERT INTO NOTIFICATIONS (NotificationID, BookingID, Title, Message, Type) VALUES (%s, %s, %s, %s, %s)",
            (n["NotificationID"], n["BookingID"], n["Title"], n["Message"], n["Type"])
        )

    # Default preferences: each student (1-3) for each club (4-5)
    for student_id in [1, 2, 3, 3030, 80, 6000]:  # Added additional students
        for club_id in [4, 5, 457, 413]:  # Added additional clubs
            cursor.execute(
                "INSERT INTO NOTIFICATION_PREFS (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications) VALUES (%s, %s, %s, %s)",
                (student_id, club_id, True, False)
            )

    # Club membership
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID, IsExec) VALUES (1, 4, FALSE)")
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID, IsExec) VALUES (2, 4, FALSE)")
    # Additional memberships can be added here

    # Assign notifications to students
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (1, 1)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (3, 3)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (4, 1)")

    # Assign club event to club 4
    cursor.execute("INSERT INTO GETS_CLUB (NotificationID, ClubID) VALUES (2, 4)")

def seed_event_details_and_topics(cursor):
    # Club 1's event (BookingID 3)
    cursor.execute("""
        INSERT INTO EVENT_DETAILS (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
        VALUES (3, 'AI & Career Fair', 'Tech and career opportunities', TRUE, '', 'club', 4)
    """)
    for topic in ["Artificial Intelligence", "Career Development"]:
        cursor.execute("INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (3, %s)", (topic,))

    # Topic preferences for students
    for sid, topic in [(1, "Artificial Intelligence"), (1, "Career Development"), (2, "Artificial Intelligence")]:
        cursor.execute("INSERT INTO USER_EVENT_TOPIC_PREFS (UserID, Topic) VALUES (%s, %s)", (sid, topic))

    # Club 2's event (BookingID 4)
    cursor.execute("""
        INSERT INTO EVENT_DETAILS (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
        VALUES (4, 'Business Networking Night', 'Connect with professionals', TRUE, '', 'club', 5)
    """)
    for topic in ["Career Development", "Entrepreneurship"]:
        cursor.execute("INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (4, %s)", (topic,))

    # Add student 3's preference for Entrepreneurship
    cursor.execute("INSERT INTO USER_EVENT_TOPIC_PREFS (UserID, Topic) VALUES (3, 'Entrepreneurship')")

    # Additional events from dev_seed
    additional_events = [
        (101, "Hackathon", "Annual student hackathon", True, "https://hackathon.com", "club", 4),
        (102, "AI Conference", "Talks on AI", True, "https://ai.com", "university", None),
        (103, "Mental Health", "Well-being workshop", True, "", "club", 5),
        (104, "Startup Pitch", "Entrepreneurship night", True, "https://startup.com", "club", 4),
        (105, "Green Day", "Sustainability event", True, "", "university", None),
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
    
    cursor.executemany(
        """INSERT INTO EVENT_DETAILS 
        (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        additional_events
    )

    # Additional topics from dev_seed
    additional_topics = [
        (101, "Hackathon"),
        (102, "Artificial Intelligence"),
        (103, "Mental Health"),
        (104, "Entrepreneurship"),
        (105, "Sustainability"),
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
        additional_topics
    )

def seed_course_data(cursor):
    # Insert course entries
    courses = [
        (1, "CPSC 471", "1", "Lecture"),
        (2, "CPSC 471", "1", "Tutorial"),
        (3, "CPSC 471", "1", "Lab"),
        (4, "PHIL 279", "1", "Lecture")
    ]
    cursor.executemany(
        "INSERT INTO COURSE (CourseID, CourseName, SessionID, Type) VALUES (%s, %s, %s, %s)",
        courses
    )