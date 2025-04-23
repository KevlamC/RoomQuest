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
        seed_course_search(cursor)
        seed_event_search(cursor)
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
        {"ID": 3030, "Email": "tcp@example.com", "Username": "tcp", "Password": "pass123", "userType": "student"},
        {"ID": 80, "Email": "http@example.com", "Username": "http", "Password": "pass123", "userType": "student"},
        {"ID": 6000, "Email": "host@example.com", "Username": "host", "Password": "pass123", "userType": "student"},
        {"ID": 457, "Email": "wics@example.com", "Username": "wics", "Password": "clubpass", "userType": "club"},
        {"ID": 413, "Email": "data@example.com", "Username": "data", "Password": "clubpass", "userType": "club"},
        {"ID": 987654321, "Email": "admin@example.com", "Username": "admin1", "Password": "adminpass", "userType": "admin"},
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
        {"RoomNumber": "151", "Building": "Engineering", "Capacity": 50, "Features": []},
        {"RoomNumber": "251", "Building": "Science", "Capacity": 100, "Features": []},
        {"RoomNumber": "353", "Building": "Health Center", "Capacity": 30, "Features": []},
        {"RoomNumber": "150", "Building": "Business", "Capacity": 40, "Features": []},
        {"RoomNumber": "230", "Building": "Community Hall", "Capacity": 200, "Features": []},
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
        {"UserID": 1, "Date": "2025-05-06", "Hour": "10:00:00", "Duration": 2, "RoomNumber": "151", "Building": "Engineering", "BookingType": "student", "CourseID": None, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-07", "Hour": "11:00:00", "Duration": 1, "RoomNumber": "251", "Building": "Science", "BookingType": "student", "CourseID": None, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-08", "Hour": "09:00:00", "Duration": 2, "RoomNumber": "353", "Building": "Health Center", "BookingType": "student", "CourseID": None, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-09", "Hour": "12:00:00", "Duration": 1, "RoomNumber": "150", "Building": "Business", "BookingType": "student", "CourseID": None, "IsApproved": False},
        {"UserID": 1, "Date": "2025-05-10", "Hour": "13:00:00", "Duration": 2, "RoomNumber": "230", "Building": "Community Hall", "BookingType": "student", "CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-11", "Hour": "14:00:00", "Duration": 2, "RoomNumber": "151", "Building": "Engineering", "BookingType": "club_event", "CourseID": None, "IsApproved": False},
        {"UserID": 5, "Date": "2025-05-12", "Hour": "15:00:00", "Duration": 2, "RoomNumber": "251", "Building": "Science", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-13", "Hour": "10:00:00", "Duration": 1, "RoomNumber": "353", "Building": "Health Center", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-14", "Hour": "11:00:00", "Duration": 1, "RoomNumber": "150", "Building": "Business", "BookingType": "club_event", "CourseID": None, "IsApproved": False},
        {"UserID": 5, "Date": "2025-05-15", "Hour": "09:00:00", "Duration": 2, "RoomNumber": "230", "Building": "Community Hall", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-16", "Hour": "10:00:00", "Duration": 2, "RoomNumber": "151", "Building": "Engineering", "BookingType": "university_event", "CourseID": None, "IsApproved": False},
        {"UserID": 2, "Date": "2025-05-17", "Hour": "13:00:00", "Duration": 2, "RoomNumber": "251", "Building": "Science", "BookingType": "student", "CourseID": None, "IsApproved": False},
        {"UserID": 3, "Date": "2025-05-18", "Hour": "09:00:00", "Duration": 2, "RoomNumber": "353", "Building": "Health Center", "BookingType": "student", "CourseID": None, "IsApproved": False},
        {"UserID": 987654321, "Date": "2025-05-19", "Hour": "12:00:00", "Duration": 1, "RoomNumber": "150", "Building": "Business", "BookingType": "university_event", "CourseID": None, "IsApproved": False},
        {"UserID": 2, "Date": "2025-05-20", "Hour": "13:00:00", "Duration": 2, "RoomNumber": "230", "Building": "Community Hall", "BookingType": "student", "CourseID": None, "IsApproved": False},
        {"UserID": 4, "Date": "2025-05-01", "Hour": "10:00:00", "Duration": 4, "RoomNumber": "151", "Building": "Engineering", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-02", "Hour": "13:00:00", "Duration": 2, "RoomNumber": "251", "Building": "Science", "BookingType": "university_event", "CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-03", "Hour": "14:00:00", "Duration": 3, "RoomNumber": "353", "Building": "Health Center", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 4, "Date": "2025-05-04", "Hour": "11:00:00", "Duration": 3, "RoomNumber": "150", "Building": "Business", "BookingType": "club_event", "CourseID": None, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-05", "Hour": "09:00:00", "Duration": 2, "RoomNumber": "230", "Building": "Community Hall", "BookingType": "university_event", "CourseID": None, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-06-01", "Hour": "09:00:00", "Duration": 2, "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 1, "IsApproved": True, "PointsAwarded": True},
        {"UserID": 987654321, "Date": "2025-06-02", "Hour": "10:00:00", "Duration": 1, "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 2, "IsApproved": True, "PointsAwarded": True},
        {"UserID": 987654321, "Date": "2025-06-03", "Hour": "11:00:00", "Duration": 2, "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 3, "IsApproved": True, "PointsAwarded": True},
        {"UserID": 987654321, "Date": "2025-06-04", "Hour": "13:00:00", "Duration": 1, "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 4, "IsApproved": True, "PointsAwarded": True}
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

    # Club 2’s event (BookingID 4)
    cursor.execute("""
        INSERT INTO EVENT_DETAILS (BookingID,ClubID,EventType,EventName)
        VALUES (4,5,'club','Business Networking Night')
    """)
    for topic in ["Career Development","Entrepreneurship"]:
        cursor.execute("INSERT INTO EVENT_TOPICS (BookingID,Topic) VALUES (4,%s)", (topic,))

def seed_event_search(cursor):
    # First ensure clubs exist (using INSERT IGNORE to avoid duplicates)
    clubs = [
        {"ID": 4, "Points": 100},
        {"ID": 5, "Points": 100}
    ]
    cursor.executemany("INSERT IGNORE INTO CLUB (ID, Points) VALUES (%s, %s)", clubs)

    # Mapping of valid event BookingIDs from your timeslots data
    # Format: {BookingID: {"UserID": x, "BookingType": "club_event/university_event"}}
    valid_event_bookings = {
        # From your timeslots data where BookingType is club_event/university_event
        3: {"UserID": 4, "BookingType": "club_event"},
        4: {"UserID": 5, "BookingType": "club_event"},
        10: {"UserID": 5, "BookingType": "club_event"},
        11: {"UserID": 5, "BookingType": "club_event"},
        12: {"UserID": 5, "BookingType": "club_event"},
        13: {"UserID": 5, "BookingType": "club_event"},
        14: {"UserID": 5, "BookingType": "club_event"},
        15: {"UserID": 987654321, "BookingType": "university_event"},
        18: {"UserID": 987654321, "BookingType": "university_event"},
        20: {"UserID": 4, "BookingType": "club_event"},
        21: {"UserID": 987654321, "BookingType": "university_event"},
        22: {"UserID": 5, "BookingType": "club_event"},
        23: {"UserID": 4, "BookingType": "club_event"},
        25: {"UserID": 987654321, "BookingType": "university_event"},
        26: {"UserID": 987654321, "BookingType": "university_event"},
        27: {"UserID": 987654321, "BookingType": "university_event"},
        28: {"UserID": 987654321, "BookingType": "university_event"}
    }

    # Your complete event data (unchanged)
    events = [
        # Club Events
        {"BookingID": 3, "EventName": "AI & Career Fair", "Description": "Tech and career opportunities", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 4},
        {"BookingID": 4, "EventName": "Business Networking Night", "Description": "Connect with professionals", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 10, "EventName": "Tech Showcase", "Description": "Cool club inventions", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 11, "EventName": "Robotics Demo", "Description": "Robot competition", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 12, "EventName": "Gaming Night", "Description": "Board and video games", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 13, "EventName": "Art Expo", "Description": "Art from our members", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 14, "EventName": "Dance Workshop", "Description": "Club-led dance class", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 5},
        {"BookingID": 20, "EventName": "Hackathon", "Description": "Annual student hackathon", "IsPublic": True, "Link": "https://hackathon.com", "EventType": "club", "ClubID": 4},
        {"BookingID": 22, "EventName": "Startup Pitch", "Description": "Entrepreneurship night", "IsPublic": True, "Link": "https://startup.com", "EventType": "club", "ClubID": 5},
        {"BookingID": 23, "EventName": "Exam Prep", "Description": "Final exam help session", "IsPublic": True, "Link": "", "EventType": "club", "ClubID": 4},
        
        # University Events
        {"BookingID": 15, "EventName": "AI Conference", "Description": "Talks on AI", "IsPublic": True, "Link": "https://ai.com", "EventType": "university", "ClubID": None},
        {"BookingID": 18, "EventName": "Mental Wellness", "Description": "De-stress tips", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None},
        {"BookingID": 21, "EventName": "Career Fair", "Description": "Meet industry reps", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None},
        {"BookingID": 25, "EventName": "Green Day", "Description": "Sustainability event", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None},
        {"BookingID": 26, "EventName": "Student Meetup", "Description": "Make new friends", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None},
        {"BookingID": 27, "EventName": "Open House", "Description": "Campus-wide event", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None},
        {"BookingID": 28, "EventName": "Workshop: Study Skills", "Description": "Tips for academic success", "IsPublic": True, "Link": "", "EventType": "university", "ClubID": None}
    ]

    # Insert events that have valid bookings
    for event in events:
        if event["BookingID"] in valid_event_bookings:
            booking_info = valid_event_bookings[event["BookingID"]]
            cursor.execute(
                """INSERT INTO EVENT_DETAILS 
                (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (event["BookingID"], 
                 event["EventName"], 
                 event["Description"],
                 event["IsPublic"],
                 event["Link"],
                 event["EventType"],
                 booking_info["UserID"] if event["EventType"] == "club" else None)
            )

    # Your complete topic data (unchanged)
    topics = [
        {"BookingID": 3, "Topic": "Artificial Intelligence"},
        {"BookingID": 3, "Topic": "Career Development"},
        {"BookingID": 4, "Topic": "Entrepreneurship"},
        {"BookingID": 4, "Topic": "Networking"},
        {"BookingID": 10, "Topic": "Technology"},
        {"BookingID": 11, "Topic": "Robotics"},
        {"BookingID": 12, "Topic": "Gaming"},
        {"BookingID": 13, "Topic": "Art"},
        {"BookingID": 14, "Topic": "Dance"},
        {"BookingID": 20, "Topic": "Hackathon"},
        {"BookingID": 22, "Topic": "Entrepreneurship"},
        {"BookingID": 23, "Topic": "Study Help"},
        {"BookingID": 15, "Topic": "Artificial Intelligence"},
        {"BookingID": 18, "Topic": "Mental Health"},
        {"BookingID": 21, "Topic": "Career Development"},
        {"BookingID": 25, "Topic": "Sustainability"},
        {"BookingID": 26, "Topic": "Community"},
        {"BookingID": 27, "Topic": "Campus Life"},
        {"BookingID": 28, "Topic": "Study Skills"}
    ]

    # Insert topics for events that exist
    for topic in topics:
        if topic["BookingID"] in valid_event_bookings:
            cursor.execute(
                "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
                (topic["BookingID"], topic["Topic"])
            )

def seed_course_search(cursor):
    # Clean COURSE and related course-linked TIME_SLOTs
    cursor.execute("DELETE FROM COURSE;")

    # Insert course entries (CourseName + SessionID = composite for uniqueness)
    courses = [
        {"CourseID": 1, "CourseName": "CPSC 471", "SessionID": "1", "Type": "Lecture"},
        {"CourseID": 2, "CourseName": "CPSC 471", "SessionID": "1", "Type": "Tutorial"},
        {"CourseID": 3, "CourseName": "CPSC 471", "SessionID": "1", "Type": "Lab"},
        {"CourseID": 4, "CourseName": "PHIL 279", "SessionID": "1", "Type": "Lecture"}
    ]
    cursor.executemany(
        "INSERT INTO COURSE (CourseID, CourseName, SessionID, Type) VALUES (%s, %s, %s, %s)",
        courses
    )