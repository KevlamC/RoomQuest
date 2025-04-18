from flask import Blueprint, jsonify
from backend.config import get_connection

init_db_bp = Blueprint('init_db', __name__)

@init_db_bp.route('/init-db', methods=['GET'])
def init_db():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Drop all tables if they exist (you might want to order this properly if foreign key constraints apply)
        cursor.execute("DROP TABLE IF EXISTS IS_MEMBER;")
        cursor.execute("DROP TABLE IF EXISTS GETS_CLUB;")
        cursor.execute("DROP TABLE IF EXISTS GETS_STUDENT;")
        cursor.execute("DROP TABLE IF EXISTS POINTS_TRANSACTION;")
        cursor.execute("DROP TABLE IF EXISTS NOTIFICATIONS;")
        cursor.execute("DROP TABLE IF EXISTS FEATURES;")
        cursor.execute("DROP TABLE IF EXISTS TIME_SLOT;")
        cursor.execute("DROP TABLE IF EXISTS COURSE;")
        cursor.execute("DROP TABLE IF EXISTS STUDENT;")
        cursor.execute("DROP TABLE IF EXISTS ADMIN;")
        cursor.execute("DROP TABLE IF EXISTS CLUB;")
        cursor.execute("DROP TABLE IF EXISTS USER;")
        cursor.execute("DROP TABLE IF EXISTS ROOMS;")

        # Recreate all tables
        cursor.execute("""
        CREATE TABLE USER (
            ID INT PRIMARY KEY,
            Email VARCHAR(255) UNIQUE NOT NULL,
            Username VARCHAR(255) UNIQUE NOT NULL,
            Password VARCHAR(255) UNIQUE NOT NULL,
            userType ENUM('student', 'admin', 'club') DEFAULT 'student'
        );
        """)

        cursor.execute("""
        CREATE TABLE ADMIN (
            ID INT PRIMARY KEY,
            FOREIGN KEY (ID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE STUDENT (
            ID INT PRIMARY KEY,
            Points INT,
            FOREIGN KEY (ID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE CLUB (
            ID INT PRIMARY KEY,
            Points INT,
            FOREIGN KEY (ID) REFERENCES USER(ID) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE ROOMS (
            RoomNumber VARCHAR(255),
            Building VARCHAR(255),
            PRIMARY KEY (RoomNumber, Building)
        );
        """)

        cursor.execute("""
        CREATE TABLE FEATURES (
            RoomNumber VARCHAR(255),
            Building VARCHAR(255),
            Feature_Name VARCHAR(255),
            PRIMARY KEY (RoomNumber, Building, Feature_Name),
            FOREIGN KEY (RoomNumber, Building) REFERENCES ROOMS(RoomNumber, Building)
                ON DELETE CASCADE ON UPDATE CASCADE
        );

        """)

        cursor.execute("""
        CREATE TABLE COURSE (
            CourseID INT PRIMARY KEY,
            Name VARCHAR(255) NOT NULL,
            Date DATE,
            Hour TIME,
            Duration INT,
            Type VARCHAR(255),
            SessionID INT
        );
        """)

        cursor.execute("""
        CREATE TABLE TIME_SLOT (
            BookingID INT PRIMARY KEY,
            UserID INT,
            Date DATE,
            Hour TIME,
            Duration INT,
            RoomNumber VARCHAR(255),
            Building VARCHAR(255),
            BookingType VARCHAR(255),
            FOREIGN KEY (UserID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (RoomNumber, Building) REFERENCES ROOMS(RoomNumber, Building)
                ON DELETE CASCADE ON UPDATE CASCADE
        );


        cursor.execute("""
        CREATE TABLE NOTIFICATIONS (
            NotificationID INT PRIMARY KEY,
            BookingID INT,
            Date DATE,
            Hour TIME,
            RoomNumber VARCHAR(255),
            Building VARCHAR(255),
            FOREIGN KEY (BookingID) REFERENCES TIME_SLOT(BookingID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (RoomNumber, Building) REFERENCES ROOMS(RoomNumber, Building)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE GETS_STUDENT (
            NotificationID INT,
            StudentID INT,
            PRIMARY KEY (NotificationID, StudentID),
            FOREIGN KEY (NotificationID) REFERENCES NOTIFICATIONS(NotificationID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (StudentID) REFERENCES STUDENT(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE GETS_CLUB (
            NotificationID INT,
            ClubID INT,
            PRIMARY KEY (NotificationID, ClubID),
            FOREIGN KEY (NotificationID) REFERENCES NOTIFICATIONS(NotificationID)
                ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ClubID) REFERENCES USER(ID)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE IS_MEMBER (
            StudentID INT,
            ClubID INT,
            IsExec BOOLEAN,
            PRIMARY KEY (StudentID, ClubID),
            FOREIGN KEY (StudentID) REFERENCES STUDENT(ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ClubID) REFERENCES CLUB(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE POINTS_TRANSACTION (
            TransactionID INT PRIMARY KEY,
            StudentID INT,
            PointsChange INT,
            TransactionDate DATETIME,
            Description VARCHAR(255),
            FOREIGN KEY (StudentID) REFERENCES STUDENT(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "All tables created successfully."})
    
    except Exception as e:
        return jsonify({"message": "Error occurred", "error": str(e)})
