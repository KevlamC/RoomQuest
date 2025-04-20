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
        {"ID": 4, "Email": "club1@example.com", "Username": "club1", "Password": "password4", "userType": "club"},
        {"ID": 5, "Email": "club2@example.com", "Username": "club2", "Password": "password5", "userType": "club"},
    ]
    for user in users:
        cursor.execute("""
            INSERT INTO USER (ID, Email, Username, Password, userType)
            VALUES (%s, %s, %s, %s, %s)
        """, (user["ID"], user["Email"], user["Username"], user["Password"], user["userType"]))

        if user["userType"] == "student":
            cursor.execute("INSERT INTO STUDENT (ID, Points) VALUES (%s, 0)", (user["ID"],))
        elif user["userType"] == "club":
            cursor.execute("INSERT INTO CLUB (ID, Points) VALUES (%s, 0)", (user["ID"],))

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
         "Features": ["dual projectors", "soundproofing"]},
        {"RoomNumber": "606", "Building": "Medicine", "Capacity": 35,
         "Features": ["whiteboard", "lab equipment"]},
        {"RoomNumber": "707", "Building": "Law", "Capacity": 50,
         "Features": ["projector", "recording setup"]},
        {"RoomNumber": "808", "Building": "Fine Arts", "Capacity": 18,
         "Features": ["soundproofing", "microphone"]},
        {"RoomNumber": "909", "Building": "IT", "Capacity": 28,
         "Features": ["computers", "projector"]},
        {"RoomNumber": "100A", "Building": "Commerce", "Capacity": 32,
         "Features": ["whiteboard", "dual projectors", "computers"]},
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
    cursor.execute("DELETE FROM TIME_SLOT;")

    timeslots = [
        {
            "UserID": 1,
            "Date": "2025-04-20",
            "Hour": "19:00",
            "Duration": 2,
            "RoomNumber": "101",
            "Building": "Engineering",
            "BookingType": "student",
            "CourseID": None,
            "IsApproved": True
        },
        {
            "UserID": 2,
            "Date": "2025-04-20",
            "Hour": "19:00",
            "Duration": 1,
            "RoomNumber": "202",
            "Building": "Science",
            "BookingType": "student",
            "CourseID": None,
            "IsApproved": False
        },
        {
            "UserID": 4,
            "Date": "2025-04-20",
            "Hour": "19:00",
            "Duration": 2,
            "RoomNumber": "303",
            "Building": "Library",
            "BookingType": "club",
            "CourseID": None,
            "IsApproved": True
        },
        {
            "UserID": 5,
            "Date": "2025-04-20",
            "Hour": "19:00",
            "Duration": 1,
            "RoomNumber": "606",
            "Building": "Medicine",
            "BookingType": "club",
            "CourseID": None,
            "IsApproved": False
        },
        {
            "UserID": 3,
            "Date": "2025-04-20",
            "Hour": "19:00",
            "Duration": 1,
            "RoomNumber": "100A",
            "Building": "Commerce",
            "BookingType": "student",
            "CourseID": None,
            "IsApproved": True
        },
    ]

    for ts in timeslots:
        cursor.execute("""
            INSERT INTO TIME_SLOT
              (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ts["UserID"],
            ts["Date"],
            ts["Hour"],
            ts["Duration"],
            ts["RoomNumber"],
            ts["Building"],
            ts["BookingType"],
            ts["CourseID"],
            ts["IsApproved"]
        ))
