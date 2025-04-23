from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from backend.config import get_connection

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed', methods=['GET'])
def run_seeding():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Clear all data first (in proper order to avoid FK constraints)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM GETS_CLUB;")
        cursor.execute("DELETE FROM GETS_STUDENT;")
        cursor.execute("DELETE FROM IS_MEMBER;")
        cursor.execute("DELETE FROM USER_EVENT_TOPIC_PREFS;")
        cursor.execute("DELETE FROM NOTIFICATION_PREFS;")
        cursor.execute("DELETE FROM NOTIFICATIONS;")
        cursor.execute("DELETE FROM EVENT_TOPICS;")
        cursor.execute("DELETE FROM EVENT_DETAILS;")
        cursor.execute("DELETE FROM POINTS_TRANSACTION;")
        cursor.execute("DELETE FROM TIME_SLOT;")
        cursor.execute("DELETE FROM FEATURES;")
        cursor.execute("DELETE FROM COURSE;")
        cursor.execute("DELETE FROM STUDENT;")
        cursor.execute("DELETE FROM CLUB;")
        cursor.execute("DELETE FROM ADMIN;")
        cursor.execute("DELETE FROM USER;")
        cursor.execute("DELETE FROM ROOMS;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        # Seed data in proper order
        seed_users(cursor)
        seed_rooms_and_features(cursor)
        seed_courses(cursor)
        seed_timeslots(cursor)
        seed_event_details_and_topics(cursor)
        seed_notifications_and_prefs(cursor)
        
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
        # Admin user
        {"ID": 987654321, "Email": "admin@university.edu", "Username": "admin1", "Password": "adminpass123", "userType": "admin"},
        
        # Students
        {"ID": 1, "Email": "student1@x.com", "Username": "s1", "Password": "p1", "userType": "student"},
        {"ID": 2, "Email": "student2@x.com", "Username": "s2", "Password": "p2", "userType": "student"},
        {"ID": 3, "Email": "student3@x.com", "Username": "s3", "Password": "p3", "userType": "student"},
        {"ID": 4, "Email": "student4@x.com", "Username": "s4", "Password": "p4", "userType": "student"},
        
        # Clubs
        {"ID": 101, "Email": "csclub@x.com", "Username": "csclub", "Password": "club123", "userType": "club"},
        {"ID": 102, "Email": "robotics@x.com", "Username": "robotics", "Password": "club123", "userType": "club"},
        {"ID": 103, "Email": "debate@x.com", "Username": "debate", "Password": "club123", "userType": "club"}
    ]
    
    for u in users:
        cursor.execute(
            "INSERT INTO USER (ID, Email, Username, Password, userType) VALUES (%s, %s, %s, %s, %s)",
            (u["ID"], u["Email"], u["Username"], u["Password"], u["userType"])
        )
        if u["userType"] == "student":
            cursor.execute("INSERT INTO STUDENT (ID, Points) VALUES (%s, 100)", (u["ID"],))
        elif u["userType"] == "club":
            cursor.execute("INSERT INTO CLUB (ID, Points) VALUES (%s, 500)", (u["ID"],))
        elif u["userType"] == "admin":
            cursor.execute("INSERT INTO ADMIN (ID) VALUES (%s)", (u["ID"],))

def seed_rooms_and_features(cursor):
    rooms = [
        {"RoomNumber": "101", "Building": "Engineering", "Capacity": 30, 
         "Features": ["whiteboard", "projector", "soundproofing"]},
        {"RoomNumber": "202", "Building": "Science", "Capacity": 25, 
         "Features": ["lab equipment", "computers"]},
        {"RoomNumber": "303", "Building": "Library", "Capacity": 20, 
         "Features": ["whiteboard", "computers"]},
        {"RoomNumber": "404", "Building": "Business", "Capacity": 40, 
         "Features": ["projector", "microphone"]},
        {"RoomNumber": "505", "Building": "Arts", "Capacity": 15, 
         "Features": ["dual projectors", "soundproofing"]}
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

def seed_courses(cursor):
    courses = [
        {"CourseID": 1, "CourseName": "CS 101", "SessionID": 1, "Type": "Lecture"},
        {"CourseID": 2, "CourseName": "CS 101", "SessionID": 1, "Type": "Lab"},
        {"CourseID": 3, "CourseName": "MATH 201", "SessionID": 1, "Type": "Lecture"},
        {"CourseID": 4, "CourseName": "PHIL 101", "SessionID": 1, "Type": "Lecture"}
    ]
    
    for course in courses:
        cursor.execute(
            "INSERT INTO COURSE (CourseID, CourseName, SessionID, Type) VALUES (%s, %s, %s, %s)",
            (course["CourseID"], course["CourseName"], course["SessionID"], course["Type"])
        )

def seed_timeslots(cursor):
    # Base timeslots (will get auto-incremented BookingIDs starting from 1)
    timeslots = [
        # Student bookings
        {"UserID": 1, "Date": "2025-04-22", "Hour": "15:00:00", "Duration": 2,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "student", 
         "CourseID": None, "PointsAwarded": True, "IsApproved": True},
         
        {"UserID": 2, "Date": "2025-04-23", "Hour": "10:00:00", "Duration": 1,
         "RoomNumber": "202", "Building": "Science", "BookingType": "student", 
         "CourseID": None, "PointsAwarded": True, "IsApproved": False},
         
        # Club events
        {"UserID": 101, "Date": "2025-04-24", "Hour": "18:00:00", "Duration": 3,
         "RoomNumber": "303", "Building": "Library", "BookingType": "club_event", 
         "CourseID": None, "PointsAwarded": True, "IsApproved": True},
         
        {"UserID": 102, "Date": "2025-04-25", "Hour": "19:00:00", "Duration": 2,
         "RoomNumber": "404", "Building": "Business", "BookingType": "club_event", 
         "CourseID": None, "PointsAwarded": True, "IsApproved": True},
         
        # University events (admin)
        {"UserID": 987654321, "Date": "2025-04-26", "Hour": "12:00:00", "Duration": 4,
         "RoomNumber": "505", "Building": "Arts", "BookingType": "university_event", 
         "CourseID": None, "PointsAwarded": True, "IsApproved": True},
         
        # Course-related bookings
        {"UserID": 987654321, "Date": "2025-04-27", "Hour": "09:00:00", "Duration": 2,
         "RoomNumber": "101", "Building": "Engineering", "BookingType": "university_event", 
         "CourseID": 1, "PointsAwarded": True, "IsApproved": True}
    ]
    
    for ts in timeslots:
        cursor.execute(
            """INSERT INTO TIME_SLOT 
            (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, PointsAwarded, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (ts["UserID"], ts["Date"], ts["Hour"], ts["Duration"],
             ts["RoomNumber"], ts["Building"], ts["BookingType"],
             ts["CourseID"], ts["PointsAwarded"], ts["IsApproved"])
        )

def seed_event_details_and_topics(cursor):
    # Get all club_event and university_event bookings
    cursor.execute("SELECT BookingID, UserID, BookingType FROM TIME_SLOT WHERE BookingType IN ('club_event', 'university_event')")
    event_bookings = cursor.fetchall()
    
    # Create events for each booking
    for booking in event_bookings:
        booking_id, user_id, booking_type = booking
        
        if booking_type == "club_event":
            # Club events
            event_data = [
                (3, "CS Club Workshop", "Weekly coding workshop", True, "", "club", 101),
                (4, "Robotics Demo", "Robot building demonstration", True, "", "club", 102)
            ]
            
            # Find matching event data for this booking
            event = next((e for e in event_data if e[0] == booking_id), None)
            if event:
                cursor.execute(
                    """INSERT INTO EVENT_DETAILS 
                    (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (booking_id, event[1], event[2], event[3], event[4], event[5], event[6])
                )
                
                # Add topics based on event type
                if "Workshop" in event[1]:
                    topics = ["Programming", "Education"]
                else:
                    topics = ["Robotics", "Engineering"]
                
                for topic in topics:
                    cursor.execute(
                        "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
                        (booking_id, topic)
                    )
        else:
            # University events
            cursor.execute(
                """INSERT INTO EVENT_DETAILS 
                (BookingID, EventName, Description, IsPublic, Link, EventType, ClubID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (booking_id, "Career Fair", "Annual university career fair", True, "", "university", None)
            )
            cursor.execute(
                "INSERT INTO EVENT_TOPICS (BookingID, Topic) VALUES (%s, %s)",
                (booking_id, "Career Development")
            )
    
    # Add user topic preferences
    topic_prefs = [
        (1, "Programming"), (1, "Career Development"),
        (2, "Robotics"), (2, "Engineering"),
        (3, "Education"), (4, "Career Development")
    ]
    
    for pref in topic_prefs:
        cursor.execute(
            "INSERT INTO USER_EVENT_TOPIC_PREFS (UserID, Topic) VALUES (%s, %s)",
            pref
        )

def seed_notifications_and_prefs(cursor):
    # Seed notifications
    notifications = [
        {"BookingID": 1, "Title": "Booking Approved", "Message": "Your booking for Engineering 101 was approved", "Type": "booking_approved"},
        {"BookingID": 3, "Title": "New Club Event", "Message": "CS Club Workshop is happening Friday", "Type": "club_event"},
        {"BookingID": None, "Title": "System Maintenance", "Message": "System will be down Sunday", "Type": "university_event"}
    ]
    
    for n in notifications:
        cursor.execute(
            "INSERT INTO NOTIFICATIONS (BookingID, Title, Message, Type) VALUES (%s, %s, %s, %s)",
            (n["BookingID"], n["Title"], n["Message"], n["Type"])
        )
    
    # Notification preferences
    for student_id in [1, 2, 3, 4]:
        for club_id in [101, 102, 103]:
            cursor.execute(
                """INSERT INTO NOTIFICATION_PREFS 
                (StudentID, ClubID, WantsClubNotifications, WantsUniversityNotifications)
                VALUES (%s, %s, %s, %s)""",
                (student_id, club_id, True, True)
            )
    
    # Club memberships
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID, IsExec) VALUES (1, 101, TRUE)")
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID, IsExec) VALUES (2, 101, FALSE)")
    cursor.execute("INSERT INTO IS_MEMBER (StudentID, ClubID, IsExec) VALUES (3, 102, TRUE)")
    
    # Assign notifications to users
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (1, 1)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (2, 1)")
    cursor.execute("INSERT INTO GETS_STUDENT (NotificationID, StudentID) VALUES (3, 2)")
    cursor.execute("INSERT INTO GETS_CLUB (NotificationID, ClubID) VALUES (2, 101)")