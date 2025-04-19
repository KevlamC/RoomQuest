from flask import Blueprint, jsonify
from datetime import date, timedelta
from backend.config import get_connection

seed_bp = Blueprint('seed', __name__)

@seed_bp.route('/seed', methods=['POST'])
def run_seeding():
    conn = get_connection()
    cursor = conn.cursor()
    try:
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
    base_user = 1
    today = date.today()
    tomorrow = today + timedelta(days=1)

    timeslots = []
    for room_number, building in [
        ("101", "Engineering"), ("202", "Science"), ("303", "Library"),
        ("404", "Business"), ("505", "Arts"), ("606", "Medicine"),
        ("707", "Law"), ("808", "Fine Arts"), ("909", "IT"), ("100A", "Commerce")
    ]:
        timeslots.append({
            "UserID": base_user, "Date": today.isoformat(), "Hour": "09:00",
            "Duration": 2, "RoomNumber": room_number, "Building": building,
            "BookingType": "student", "CourseID": None, "IsApproved": True
        })
        timeslots.append({
            "UserID": base_user, "Date": today.isoformat(), "Hour": "14:00",
            "Duration": 1, "RoomNumber": room_number, "Building": building,
            "BookingType": "student", "CourseID": None, "IsApproved": True
        })
        timeslots.append({
            "UserID": base_user, "Date": tomorrow.isoformat(), "Hour": "11:00",
            "Duration": 3, "RoomNumber": room_number, "Building": building,
            "BookingType": "club", "CourseID": None, "IsApproved": False
        })

    cursor.execute("DELETE FROM TIME_SLOT;")

    for ts in timeslots:
        cursor.execute("""
            INSERT INTO TIME_SLOT
              (UserID, Date, Hour, Duration, RoomNumber, Building, BookingType, CourseID, IsApproved)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            ts["UserID"], ts["Date"], ts["Hour"], ts["Duration"],
            ts["RoomNumber"], ts["Building"], ts["BookingType"],
            ts["CourseID"], ts["IsApproved"]
        ))
