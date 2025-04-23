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
        seed_course_search(cursor)  # Move this before seed_timeslots
        seed_timeslots(cursor)      # Now it can reference existing courses
        seed_notifications_and_prefs(cursor)
        seed_event_details_and_topics(cursor)
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
    cursor.execute("DELETE FROM USER")
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
    student_rows = [(u["ID"], 0) for u in users if u["userType"] == "student"]
    club_rows = [(u["ID"], 0) for u in users if u["userType"] == "club"]
    
    if student_rows:
        cursor.executemany("INSERT INTO STUDENT (ID, Points) VALUES (%s, %s)", student_rows)
    if club_rows:
        cursor.executemany("INSERT INTO CLUB (ID, Points) VALUES (%s, %s)", club_rows)


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
    feature_rows = [
        (room["RoomNumber"], room["Building"], feat)
        for room in rooms
        for feat in room["Features"]
    ]
    if feature_rows:
        cursor.executemany(
            "INSERT INTO FEATURES (RoomNumber, Building, Feature_Name) VALUES (%s, %s, %s)",
            feature_rows,
        )


def seed_timeslots(cursor):
    cursor.execute("DELETE FROM TIME_SLOT")
    timeslots = [
        {"UserID": 1, "Date": "2025-04-22", "Hour": "15:00:00", "Duration": 3,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 2, "Date": "2025-04-22", "Hour": "15:00:00", "Duration": 3,
         "RoomNumber": "202", "Building": "Science", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 4, "Date": "2025-04-23", "Hour": "18:00:00", "Duration": 2,
         "RoomNumber": "303", "Building": "Library", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 5, "Date": "2025-04-24", "Hour": "19:00:00", "Duration": 4,
         "RoomNumber": "404", "Building": "Business", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-06", "Hour": "10:00:00", "Duration": 2,
         "RoomNumber": "151", "Building": "Engineering", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-07", "Hour": "11:00:00", "Duration": 1,
         "RoomNumber": "251", "Building": "Science", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-08", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "353", "Building": "Health Center", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 1, "Date": "2025-05-09", "Hour": "12:00:00", "Duration": 1,
         "RoomNumber": "150", "Building": "Business", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 1, "Date": "2025-05-10", "Hour": "13:00:00", "Duration": 2,
         "RoomNumber": "230", "Building": "Community Hall", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-11", "Hour": "14:00:00", "Duration": 2,
         "RoomNumber": "151", "Building": "Engineering", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 5, "Date": "2025-05-12", "Hour": "15:00:00", "Duration": 2,
         "RoomNumber": "251", "Building": "Science", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-13", "Hour": "10:00:00", "Duration": 1,
         "RoomNumber": "353", "Building": "Health Center", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-14", "Hour": "11:00:00", "Duration": 1,
         "RoomNumber": "150", "Building": "Business", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 5, "Date": "2025-05-15", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "230", "Building": "Community Hall", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-16", "Hour": "10:00:00", "Duration": 2,
         "RoomNumber": "151", "Building": "Engineering", "BookingType": "university_event", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 2, "Date": "2025-05-17", "Hour": "13:00:00", "Duration": 2,
         "RoomNumber": "251", "Building": "Science", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 3, "Date": "2025-05-18", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "353", "Building": "Health Center", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 987654321, "Date": "2025-05-19", "Hour": "12:00:00", "Duration": 1,
         "RoomNumber": "150", "Building": "Business", "BookingType": "university_event", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 2, "Date": "2025-05-20", "Hour": "13:00:00", "Duration": 2,
         "RoomNumber": "230", "Building": "Community Hall", "BookingType": "student", "CourseID": None, "PointsAwarded": True, "IsApproved": False},
        {"UserID": 4, "Date": "2025-05-01", "Hour": "10:00:00", "Duration": 4,
         "RoomNumber": "151", "Building": "Engineering", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-02", "Hour": "13:00:00", "Duration": 2,
         "RoomNumber": "251", "Building": "Science", "BookingType": "university_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 5, "Date": "2025-05-03", "Hour": "14:00:00", "Duration": 3,
         "RoomNumber": "353", "Building": "Health Center", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 4, "Date": "2025-05-04", "Hour": "11:00:00", "Duration": 3,
         "RoomNumber": "150", "Building": "Business", "BookingType": "club_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-05-05", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "230", "Building": "Community Hall", "BookingType": "university_event", "CourseID": None, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-06-01", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 1, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-06-02", "Hour": "10:00:00", "Duration": 1,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 2, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-06-03", "Hour": "11:00:00", "Duration": 2,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 3, "PointsAwarded": True, "IsApproved": True},
        {"UserID": 987654321, "Date": "2025-06-04", "Hour": "13:00:00", "Duration": 1,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", "CourseID": 4, "PointsAwarded": True, "IsApproved": True},
    ]
    for ts in timeslots:
        cursor.execute(
            "INSERT INTO TIME_SLOT (UserID,Date,Hour,Duration,RoomNumber,Building,BookingType,CourseID,PointsAwarded,IsApproved)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (ts["UserID"], ts["Date"], ts["Hour"], ts["Duration"],
             ts["RoomNumber"], ts["Building"], ts["BookingType"],
             ts["CourseID"],ts["PointsAwarded"], ts["IsApproved"])
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
    prefs_rows = [
    (student_id, club_id, True, False)
    for student_id in [1, 2, 3]
    for club_id in [4, 5]
    ]
    cursor.executemany(
        "INSERT INTO NOTIFICATION_PREFS (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications) VALUES (%s, %s, %s, %s)",
        prefs_rows,
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
        # Clean up old data
        cursor.execute("DELETE FROM CLUB;")
        cursor.execute("DELETE FROM EVENT_DETAILS;")
        cursor.execute("DELETE FROM EVENT_TOPICS;")

        # Insert clubs
        clubs = [
            {"ID": 4, "Points": 100},
            {"ID": 5, "Points": 100}
        ]
        clubs = [(club["ID"], club["Points"]) for club in clubs]
        cursor.executemany("INSERT INTO CLUB (ID, Points) VALUES (%s, %s)", clubs)

        # Insert base event details
        events = [
            {"BookingID": 3, "EventName": "Club Event A", "Description": "Description for Club Event A", "IsPublic": True, "Link": "https://example.com/club-a", "EventType": "club", "ClubID": 4},
            {"BookingID": 4, "EventName": "Club Event B", "Description": "Description for Club Event B", "IsPublic": True, "Link": "https://example.com/club-b", "EventType": "club", "ClubID": 5},
            {"BookingID": 10, "EventName": "Club Event C", "Description": "Description for Club Event C", "IsPublic": True, "Link": "https://example.com/club-c", "EventType": "club", "ClubID": 5},
            {"BookingID": 11, "EventName": "Club Event D", "Description": "Description for Club Event D", "IsPublic": True, "Link": "https://example.com/club-d", "EventType": "club", "ClubID": 5},
            {"BookingID": 12, "EventName": "Club Event E", "Description": "Description for Club Event E", "IsPublic": True, "Link": "https://example.com/club-e", "EventType": "club", "ClubID": 5},
            {"BookingID": 13, "EventName": "Club Event F", "Description": "Description for Club Event F", "IsPublic": True, "Link": "https://example.com/club-f", "EventType": "club", "ClubID": 5},
            {"BookingID": 14, "EventName": "Club Event G", "Description": "Description for Club Event G", "IsPublic": True, "Link": "https://example.com/club-g", "EventType": "club", "ClubID": 5},
            {"BookingID": 20, "EventName": "Club Event H", "Description": "Description for Club Event H", "IsPublic": True, "Link": "https://example.com/club-h", "EventType": "club", "ClubID": 4},
            {"BookingID": 22, "EventName": "Club Event I", "Description": "Description for Club Event I", "IsPublic": True, "Link": "https://example.com/club-i", "EventType": "club", "ClubID": 5},
            {"BookingID": 23, "EventName": "Club Event J", "Description": "Description for Club Event J", "IsPublic": True, "Link": "https://example.com/club-j", "EventType": "club", "ClubID": 4},

            {"BookingID": 15, "EventName": "University Event 1", "Description": "Description for University Event 1", "IsPublic": True, "Link": "https://example.com/uni-1", "EventType": "university", "ClubID": None},
            {"BookingID": 18, "EventName": "University Event 2", "Description": "Description for University Event 2", "IsPublic": True, "Link": "https://example.com/uni-2", "EventType": "university", "ClubID": None},
            {"BookingID": 21, "EventName": "University Event 3", "Description": "Description for University Event 3", "IsPublic": True, "Link": "https://example.com/uni-3", "EventType": "university", "ClubID": None},
            {"BookingID": 25, "EventName": "University Event 4", "Description": "Description for University Event 4", "IsPublic": True, "Link": "https://example.com/uni-4", "EventType": "university", "ClubID": None},
            {"BookingID": 26, "EventName": "University Event 5", "Description": "Description for University Event 5", "IsPublic": True, "Link": "https://example.com/uni-5", "EventType": "university", "ClubID": None},
            {"BookingID": 27, "EventName": "University Event 6", "Description": "Description for University Event 6", "IsPublic": True, "Link": "https://example.com/uni-6", "EventType": "university", "ClubID": None},
            {"BookingID": 28, "EventName": "University Event 7", "Description": "Description for University Event 7", "IsPublic": True, "Link": "https://example.com/uni-7", "EventType": "university", "ClubID": None},
        ]

        # Convert list of dictionaries to list of tuples for executemany
        event_rows = [
            (event["BookingID"], event["EventName"], event["Description"], event["IsPublic"], event["Link"], event["EventType"], event["ClubID"])
            for event in events
        ]
        cursor.executemany(
            """INSERT INTO EVENT_DETAILS 
            (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            event_rows,
        )

        # Insert base event topics
        topics = [
            {"BookingID": 3, "Topic": "Hackathon"},
            {"BookingID": 4, "Topic": "Artificial Intelligence"},
            {"BookingID": 10, "Topic": "Mental Health"},
            {"BookingID": 11, "Topic": "Entrepreneurship"},
            {"BookingID": 12, "Topic": "Sustainability"},
            {"BookingID": 13, "Topic": "Career Development"},
            {"BookingID": 14, "Topic": "Resumes"},
            {"BookingID": 20, "Topic": "Study Help"},
            {"BookingID": 22, "Topic": "Community"},
            {"BookingID": 23, "Topic": "Board Games"},
            {"BookingID": 15, "Topic": "Technology"},
            {"BookingID": 18, "Topic": "Robotics"},
            {"BookingID": 21, "Topic": "Gaming"},
            {"BookingID": 25, "Topic": "Art"},
            {"BookingID": 26, "Topic": "Dance"},
            {"BookingID": 27, "Topic": "Campus Life"},
            {"BookingID": 28, "Topic": "Study Skills"},
        ]
        # Convert list of dictionaries to list of tuples for executemany
        topic_rows = [(topic["BookingID"], topic["Topic"]) for topic in topics]
        cursor.executemany(
            "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
            topic_rows,
        )

def seed_course_search(cursor):
    # Clean COURSE and related course-linked TIME_SLOTs
    cursor.execute("DELETE FROM COURSE;")

    courses = [
        {"CourseName": "CPSC 471", "SessionID": 1, "Type": "Lecture"},
        {"CourseName": "CPSC 471", "SessionID": 1, "Type": "Tutorial"},
        {"CourseName": "CPSC 471", "SessionID": 1, "Type": "Lab"},
        {"CourseName": "PHIL 279", "SessionID": 1, "Type": "Lecture"}
    ]
    
    course_data = [(course["CourseName"], course["SessionID"], course["Type"]) for course in courses]
    cursor.executemany(
        "INSERT INTO COURSE (CourseName, SessionID, Type) VALUES (%s, %s, %s)",
        course_data,
    )
