from flask import Blueprint, jsonify
from datetime import date, timedelta
from backend.config import get_connection

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed', methods=['GET'])
def run_seeding():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        seed_users(cursor)
        seed_rooms_and_features(cursor)
        seed_timeslots(cursor)
        seed_notifications_and_prefs(cursor)
        seed_event_details_and_topics(cursor)
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
        {"ID": 1, "Email": "student1@x.com", "Username": "s1", "Password": "p1", "userType": "student"},
        {"ID": 2, "Email": "student2@x.com", "Username": "s2", "Password": "p2", "userType": "student"},
        {"ID": 3, "Email": "student3@x.com", "Username": "s3", "Password": "p3", "userType": "student"},
        {"ID": 4, "Email": "club1@x.com",    "Username": "c1", "Password": "p4", "userType": "club"},
        {"ID": 5, "Email": "club2@x.com",    "Username": "c2", "Password": "p5", "userType": "club"},
    ]
    for u in users:
        cursor.execute(
            "INSERT INTO USER (ID,Email,Username,Password,userType) VALUES (%s,%s,%s,%s,%s)",
            (u["ID"], u["Email"], u["Username"], u["Password"], u["userType"])
        )
        if u["userType"] == "student":
            cursor.execute("INSERT INTO STUDENT (ID,Points) VALUES (%s,0)", (u["ID"],))
        else:
            cursor.execute("INSERT INTO CLUB (ID,Points) VALUES (%s,0)", (u["ID"],))


def seed_rooms_and_features(cursor):
    rooms = [
        {"RoomNumber": "101",  "Building": "Engineering", "Capacity": 30, "Features": ["whiteboard", "projector", "soundproofing"]},
        {"RoomNumber": "202",  "Building": "Science",     "Capacity": 25, "Features": ["lab equipment", "computers"]},
        {"RoomNumber": "303",  "Building": "Library",     "Capacity": 20, "Features": ["whiteboard", "computers"]},
        {"RoomNumber": "404",  "Building": "Business",    "Capacity": 40, "Features": ["projector", "microphone"]},
        {"RoomNumber": "505",  "Building": "Arts",        "Capacity": 15, "Features": ["dual projectors", "soundproofing"]},
        {"RoomNumber": "606",  "Building": "Medicine",    "Capacity": 35, "Features": ["whiteboard", "lab equipment"]},
        {"RoomNumber": "707",  "Building": "Law",         "Capacity": 50, "Features": ["projector", "recording setup"]},
        {"RoomNumber": "808",  "Building": "Fine Arts",   "Capacity": 18, "Features": ["soundproofing", "microphone"]},
        {"RoomNumber": "909",  "Building": "IT",          "Capacity": 28, "Features": ["computers", "projector"]},
        {"RoomNumber": "100A", "Building": "Commerce",    "Capacity": 32, "Features": ["whiteboard", "dual projectors", "computers"]},
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
    timeslots = [
        {"UserID": 1, "Date": "2025-04-22", "Hour": "15:00:00", "Duration": 3,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "student",   "CourseID": None, "IsApproved": True},
        {"UserID": 2, "Date": "2025-04-22", "Hour": "15:00:00", "Duration": 3,
         "RoomNumber": "202", "Building": "Science",     "BookingType": "student",   "CourseID": None, "IsApproved": False},
        {"UserID": 4, "Date": "2025-04-23", "Hour": "18:00:00", "Duration": 2,
         "RoomNumber": "303", "Building": "Library",     "BookingType": "club_event","CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-04-24", "Hour": "19:00:00", "Duration": 4,
         "RoomNumber": "404", "Building": "Business",    "BookingType": "club_event","CourseID": None, "IsApproved": True},
    ]
    for ts in timeslots:
        cursor.execute(
            "INSERT INTO TIME_SLOT (UserID,Date,Hour,Duration,RoomNumber,Building,BookingType,CourseID,IsApproved)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (ts["UserID"], ts["Date"], ts["Hour"], ts["Duration"],
             ts["RoomNumber"], ts["Building"], ts["BookingType"],
             ts["CourseID"], ts["IsApproved"])
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
        {"NotificationID": 2, "BookingID": None, "Title": "New Club Event",   "Message": "Music Club is hosting a concert.", "Type": "club_event"},
        {"NotificationID": 3, "BookingID": None, "Title": "University Alert", "Message": "Campus will be closed tomorrow.", "Type": "university_event"},
        {"NotificationID": 4, "BookingID": None, "Title": "Points Added",     "Message": "You earned 10 points.",      "Type": "points_confirmation"},
    ]
    for n in notifications:
        cursor.execute(
            "INSERT INTO NOTIFICATIONS (NotificationID, BookingID, Title, Message, Type) VALUES (%s, %s, %s, %s, %s)",
            (n["NotificationID"], n["BookingID"], n["Title"], n["Message"], n["Type"])
        )

    # Default preferences: each student (1-3) for each club (4-5)
    for student_id in [1, 2, 3]:
        for club_id in [4, 5]:
            cursor.execute(
                "INSERT INTO NOTIFICATION_PREFS (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications) VALUES (%s, %s, %s, %s)",
                (student_id, club_id, True, False)
            )

    # Club membership
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID) VALUES (1, 4)")
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID) VALUES (2, 4)")

    # Assign notifications to students
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (1, 1)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (3, 3)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (4, 1)")

    # Assign club event to club 4
    cursor.execute("INSERT INTO GETS_CLUB (NotificationID, ClubID) VALUES (2, 4)")


def seed_event_details_and_topics(cursor):
    # Club 1’s event (BookingID 3)
    cursor.execute("""
        INSERT INTO EVENT_DETAILS (BookingID,ClubID,EventType,EventName)
        VALUES (3,4,'club','AI & Career Fair')
    """)
    for topic in ["Artificial Intelligence","Career Development"]:
        cursor.execute("INSERT INTO EVENT_TOPICS (BookingID,Topic) VALUES (3,%s)", (topic,))

    # Topic preferences for students
    for sid, topic in [(1,"Artificial Intelligence"),(1,"Career Development"),(2,"Artificial Intelligence")]:
        cursor.execute("INSERT INTO USER_EVENT_TOPIC_PREFS (UserID,Topic) VALUES (%s,%s)", (sid,topic))

    # Club 2’s event (BookingID 4)
    cursor.execute("""
        INSERT INTO EVENT_DETAILS (BookingID,ClubID,EventType,EventName)
        VALUES (4,5,'club','Business Networking Night')
    """)
    for topic in ["Career Development","Entrepreneurship"]:
        cursor.execute("INSERT INTO EVENT_TOPICS (BookingID,Topic) VALUES (4,%s)", (topic,))

    # Add student 3’s preference for Entrepreneurship
    cursor.execute("INSERT INTO USER_EVENT_TOPIC_PREFS (UserID,Topic) VALUES (3,'Entrepreneurship')")

def seed_test_data(cursor):
        # Clean up old data
        cursor.execute("DELETE FROM USER;")
        cursor.execute("DELETE FROM TIME_SLOT;")
        cursor.execute("DELETE FROM CLUB;")
        cursor.execute("DELETE FROM EVENT_DETAILS;")
        cursor.execute("DELETE FROM EVENT_TOPICS;")

        # Insert test users
        users = [
            (3030, "tcp@example.com", "tcp", "pass123", "student"),
            (80, "http@example.com", "http", "pass123", "student"),
            (6000, "host@example.com", "host", "pass123", "student"),
            (457, "wics@example.com", "wics", "clubpass", "club"),
            (413, "data@example.com", "data", "clubpass", "club"),
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
            ("151", "Engineering", 50),
            ("251", "Science", 100),
            ("353", "Health Center", 30),
            ("150", "Business", 40),
            ("230", "Community Hall", 200)
        ]
        cursor.executemany(
            "INSERT INTO ROOMS (RoomNumber, Building, Capacity) VALUES (%s, %s, %s)",
            rooms
        )

        # Insert base time slots for events.
        timeslots = [
            (501, 4, "2025-05-01", "10:00:00", 4, "151", "Engineering", "club_event", None, True, True),
            (502, 987654321, "2025-05-02", "13:00:00", 2, "251", "Science", "university_event", None, True, True),
            (503, 5, "2025-05-03", "14:00:00", 3, "353", "Health Center", "club_event", None, True, True),
            (504, 4, "2025-05-04", "11:00:00", 3, "150", "Business", "club_event", None, True, True),
            (505, 987654321, "2025-05-05", "09:00:00", 2, "230", "Community Hall", "university_event", None, True, True)
        ]
        cursor.executemany(
            """INSERT INTO TIME_SLOT 
            (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved, PointsAwarded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            timeslots
        )

        # Insert base event details
        events = [
            (501, "Hackathon", "Annual student hackathon", True, "https://hackathon.com", "club", 4),
            (502, "AI Conference", "Talks on AI", True, "https://ai.com", "university", None),
            (503, "Mental Health", "Well-being workshop", True, "", "club", 5),
            (504, "Startup Pitch", "Entrepreneurship night", True, "https://startup.com", "club", 4),
            (505, "Green Day", "Sustainability event", True, "", "university", None)
        ]
        cursor.executemany(
            """INSERT INTO EVENT_DETAILS 
            (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            events
        )

        # Insert base event topics
        topics = [
            (501, "Hackathon"),
            (502, "Artificial Intelligence"),
            (503, "Mental Health"),
            (504, "Entrepreneurship"),
            (505, "Sustainability")
        ]
        cursor.executemany(
            "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
            topics
        )

        # 15 new time slots
        extra_timeslots = [
            (506, 1, "2025-05-06", "10:00:00", 2, "101", "Engineering", "student", None, False, True),
            (507, 1, "2025-05-07", "11:00:00", 1, "201", "Science", "student", None, True, True),
            (508, 1, "2025-05-08", "09:00:00", 2, "303", "Health Center", "student", None, True, True),
            (509, 1, "2025-05-09", "12:00:00", 1, "100", "Business", "student", None, False, False),
            (510, 1, "2025-05-10", "13:00:00", 2, "200", "Community Hall", "student", None, True, True),
            (511, 5, "2025-05-11", "14:00:00", 2, "101", "Engineering", "club_event", None, False, True),
            (512, 5, "2025-05-12", "15:00:00", 2, "201", "Science", "club_event", None, True, True),
            (513, 5, "2025-05-13", "10:00:00", 1, "303", "Health Center", "club_event", None, True, True),
            (514, 5, "2025-05-14", "11:00:00", 1, "100", "Business", "club_event", None, False, False),
            (515, 5, "2025-05-15", "09:00:00", 2, "200", "Community Hall", "club_event", None, True, True),
            (516, 987654321, "2025-05-16", "10:00:00", 2, "101", "Engineering", "university_event", None, False, False),
            (517, 2, "2025-05-17", "13:00:00", 2, "201", "Science", "student", None, False, True),
            (518, 3, "2025-05-18", "09:00:00", 2, "303", "Health Center", "student", None, False, True),
            (519, 987654321, "2025-05-19", "12:00:00", 1, "100", "Business", "university_event", None, False, True),
            (520, 2, "2025-05-20", "13:00:00", 2, "200", "Community Hall", "student", None, False, True)
        ]
        cursor.executemany("""
            INSERT INTO TIME_SLOT 
            (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, extra_timeslots)

        # Matching event details
        extra_events = [
            (506, "Career Fair", "Meet industry reps", True, "", "university", None),
            (507, "Resume Workshop", "Improve your resume", True, "", "university", None),
            (508, "Exam Prep", "Final exam help session", True, "", "club", 5),
            (509, "Student Meetup", "Make new friends", True, "", "university", None),
            (510, "Chess Tournament", "Chess battles!", True, "", "university", None),
            (511, "Tech Showcase", "Cool club inventions", True, "", "club", 5),
            (512, "Robotics Demo", "Robot competition", True, "", "club", 5),
            (513, "Gaming Night", "Board and video games", True, "", "club", 5),
            (514, "Art Expo", "Art from our members", True, "", "club", 5),
            (515, "Dance Workshop", "Club-led dance class", True, "", "club", 5),
            (516, "Open House", "Campus-wide event", True, "", "university", None),
            (517, "Workshop: Study Skills", "Tips for academic success", True, "", "university", None),
            (518, "Mental Wellness", "De-stress tips", True, "", "university", None),
            (519, "Alumni Talk", "Hear from grads", True, "", "university", None),
            (520, "Coding Bootcamp", "Learn to code fast", True, "", "university", None)
        ]
        cursor.executemany("""
            INSERT INTO EVENT_DETAILS 
            (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, extra_events)

        # Matching event topics
        extra_topics = [
            (506, "Career Development"),
            (507, "Resumes"),
            (508, "Study Help"),
            (509, "Community"),
            (510, "Board Games"),
            (511, "Technology"),
            (512, "Robotics"),
            (513, "Gaming"),
            (514, "Art"),
            (515, "Dance"),
            (516, "Campus Life"),
            (517, "Study Skills"),
            (518, "Mental Health"),
            (519, "Alumni"),
            (520, "Programming")
        ]
        cursor.executemany(
            "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
            extra_topics
        )


def seed_course_search(cursor):

        # Clean COURSE and related course-linked TIME_SLOTs
        cursor.execute("DELETE FROM TIME_SLOT WHERE CourseID IS NOT NULL;")
        cursor.execute("DELETE FROM COURSE;")

        # Insert course entries (CourseName + SessionID = composite for uniqueness)
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

        # Insert TIME_SLOTs linked to courses
        slots = [
            (201, 987654321, "2025-06-01", "09:00:00", 2, "101", "Engineering", "university_event", 1, True, True),
            (202, 987654321, "2025-06-02", "10:00:00", 1, "101", "Engineering", "university_event", 2, True, True),
            (203, 987654321, "2025-06-03", "11:00:00", 2, "101", "Engineering", "university_event", 3, True, True),
            (204, 987654321, "2025-06-04", "13:00:00", 1, "101", "Engineering", "university_event", 4, True, True),
        ]
        cursor.executemany(
            """INSERT INTO TIME_SLOT
               (BookingID, UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved, PointsAwarded)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            slots
        )