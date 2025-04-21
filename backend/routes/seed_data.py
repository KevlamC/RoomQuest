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
        {"ID": 1, "Email": "student1@example.com", "Username": "student1", "Password": "password1", "userType": "student"},
        {"ID": 2, "Email": "student2@example.com", "Username": "student2", "Password": "password2", "userType": "student"},
        {"ID": 3, "Email": "student3@example.com", "Username": "student3", "Password": "password3", "userType": "student"},
        {"ID": 4, "Email": "club1@example.com",    "Username": "club1",    "Password": "password4", "userType": "club"},
        {"ID": 5, "Email": "club2@example.com",    "Username": "club2",    "Password": "password5", "userType": "club"},
        # Add your admin here if needed:
        # {"ID": 99, "Email": "youradmin@example.com", "Username": "youradmin", "Password": "securepass", "userType": "admin"},
    ]
    cursor.execute("DELETE FROM STUDENT;")
    cursor.execute("DELETE FROM CLUB;")
    cursor.execute("DELETE FROM USER;")
    for user in users:
        cursor.execute(
            "INSERT INTO USER (ID, Email, Username, Password, userType) VALUES (%s, %s, %s, %s, %s)",
            (user["ID"], user["Email"], user["Username"], user["Password"], user["userType"])
        )
        if user["userType"] == "student":
            cursor.execute(
                "INSERT INTO STUDENT (ID, Points) VALUES (%s, 0)",
                (user["ID"],)
            )
        elif user["userType"] == "club":
            cursor.execute(
                "INSERT INTO CLUB (ID, Points) VALUES (%s, 0)",
                (user["ID"],)
            )


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
    cursor.execute("DELETE FROM FEATURES;")
    cursor.execute("DELETE FROM ROOMS;")
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
        {"UserID": 1, "Date": "2025-04-20", "Hour": "15:00:00", "Duration": 3, "RoomNumber": "101",  "Building": "Engineering", "BookingType": "student", "CourseID": None, "IsApproved": True},
        {"UserID": 2, "Date": "2025-04-20", "Hour": "15:00:00", "Duration": 3, "RoomNumber": "202",  "Building": "Science",     "BookingType": "student", "CourseID": None, "IsApproved": False},
        {"UserID": 4, "Date": "2025-04-20", "Hour": "15:00:00", "Duration": 3, "RoomNumber": "303",  "Building": "Library",     "BookingType": "club",    "CourseID": None, "IsApproved": True},
        {"UserID": 5, "Date": "2025-04-20", "Hour": "15:00:00", "Duration": 3, "RoomNumber": "606",  "Building": "Medicine",    "BookingType": "club",    "CourseID": None, "IsApproved": False},
        {"UserID": 3, "Date": "2025-04-21", "Hour": "20:00:00", "Duration": 3, "RoomNumber": "100A", "Building": "Commerce",    "BookingType": "student", "CourseID": None, "IsApproved": True},
    ]
    cursor.execute("DELETE FROM TIME_SLOT;")
    for ts in timeslots:
        cursor.execute(
            "INSERT INTO TIME_SLOT (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (ts["UserID"], ts["Date"], ts["Hour"], ts["Duration"], ts["RoomNumber"], ts["Building"], ts["BookingType"], ts["CourseID"], ts["IsApproved"])
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
                (student_id, club_id, True, True)
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
