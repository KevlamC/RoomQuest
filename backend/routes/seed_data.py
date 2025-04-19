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
            cursor.execute("INSERT INTO CLUB (ID, ClubName) VALUES (%s, %s)", (user["ID"], user["Username"]))

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
    today = date.today()
    tomorrow = today + timedelta(days=1)
    user_ids = [1, 2, 3, 4, 5]  # 3 students + 2 clubs
    hour_slots = ["09:00", "10:00", "13:00", "14:00", "15:00", "16:00"]  # 6 timeslots

    rooms = [
        ("101", "Engineering"), ("202", "Science"), ("303", "Library"),
        ("404", "Business"), ("505", "Arts"), ("606", "Medicine"),
        ("707", "Law"), ("808", "Fine Arts"), ("909", "IT"), ("100A", "Commerce")
    ]

    cursor.execute("DELETE FROM TIME_SLOT;")

    for i, (room_number, building) in enumerate(rooms):
        for j, hour in enumerate(hour_slots):
            user_id = user_ids[(i + j) % len(user_ids)]
            is_club = user_id in [4, 5]
            cursor.execute("""
                INSERT INTO TIME_SLOT
                  (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                today.isoformat() if j < 3 else tomorrow.isoformat(),
                hour,
                1 if j % 2 == 0 else 2,
                room_number,
                building,
                "club" if is_club else "student",
                None,
                j % 2 == 0  # Alternate approval
            ))
