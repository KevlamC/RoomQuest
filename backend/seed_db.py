from backend.config import get_connection

def seed_database():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Example: Seed USERS
        users = [
            (1, "alice@example.com", "alice123"),
            (2, "bob@example.com", "bobby"),
        ]
        cursor.executemany("INSERT INTO USER (ID, Email, Username) VALUES (%s, %s, %s)", users)

        # Example: Seed ROOMS
        rooms = [
            (1, "101", "EDC"),
            (2, "202", "BAS"),
            (3, "303", "MC"),
        ]
        cursor.executemany("INSERT INTO ROOMS (RoomID, RoomNumber, Building) VALUES (%s, %s, %s)", rooms)

        # You can repeat similar inserts for CLUB, STUDENT, etc.

        conn.commit()
        print("Seeding complete.")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print("Error seeding database:", e)

if __name__ == "__main__":
    seed_database()
