from flask import Blueprint, jsonify
from backend.config import get_connection

init_db_bp = Blueprint('init_db', __name__)

@init_db_bp.route('/init-db', methods=['GET'])
def init_db():
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Drop in correct dependency order (child tables first)
        cursor.execute("DROP TABLE IF EXISTS GETS_CLUB;")
        cursor.execute("DROP TABLE IF EXISTS GETS_STUDENT;")
        cursor.execute("DROP TABLE IF EXISTS IS_MEMBER;")
        cursor.execute("DROP TABLE IF EXISTS NOTIFICATION_PREFS;")
        cursor.execute("DROP TABLE IF EXISTS NOTIFICATIONS;")
        cursor.execute("DROP TABLE IF EXISTS EVENT_TOPICS;")
        cursor.execute("DROP TABLE IF EXISTS EVENT_DETAILS;")
        cursor.execute("DROP TABLE IF EXISTS POINTS_TRANSACTION;")
        cursor.execute("DROP TABLE IF EXISTS TIME_SLOT;")
        cursor.execute("DROP TABLE IF EXISTS FEATURES;")
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
            Password VARCHAR(255) NOT NULL,
            userType ENUM('student', 'admin', 'club') DEFAULT 'student'
        );
        """)

        cursor.execute("""
        CREATE TABLE ADMIN (
            ID INT PRIMARY KEY,
            FOREIGN KEY (ID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        # 1. Making User of type "admin"
        cursor.execute("""
            INSERT INTO USER (ID, Email, Username, Password, userType)
            VALUES (%s, %s, %s, %s, %s)
        """, (987654321, "admin@university.edu", "admin1", "adminpass123", "admin"))
        
        # 2. Connecting that user to "admin" table
        cursor.execute("""
            INSERT INTO ADMIN (ID)
            VALUES (%s)
        """, (987654321,))

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
            Capacity INT,
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
            CourseID INT PRIMARY KEY AUTO_INCREMENT,
            CourseName VARCHAR(255),
            SessionID INT,
            Type ENUM('Lecture', 'Tutorial', 'Lab')
        );
        """)

        cursor.execute("""
        CREATE TABLE TIME_SLOT (
            BookingID INT PRIMARY KEY AUTO_INCREMENT,
            UserID INT NOT NULL,
            Date DATE NOT NULL,
            Hour TIME NOT NULL,
            Duration INT DEFAULT 1,
            RoomNumber VARCHAR(255) NOT NULL,
            Building VARCHAR(255) NOT NULL,
            BookingType ENUM('student', 'club', 'club_event', 'admin', 'university_event') NOT NULL,
            CourseID INT DEFAULT NULL,
            PointsAwarded BOOLEAN DEFAULT FALSE,
            IsApproved BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (UserID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (RoomNumber, Building) REFERENCES ROOMS(RoomNumber, Building) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (CourseID) REFERENCES COURSE(CourseID) ON DELETE SET NULL ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE EVENT_DETAILS (
          BookingID    INT PRIMARY KEY,
          EventName    VARCHAR(255) NOT NULL,
          Description  TEXT          NULL,
          IsPublic     BOOLEAN       DEFAULT TRUE,
          Link         VARCHAR(255)  NULL,
          EventType    ENUM('club', 'university') NOT NULL,
          ClubID INT NULL,
          FOREIGN KEY (ClubID) REFERENCES CLUB(ID) ON DELETE SET NULL ON UPDATE CASCADE,
          FOREIGN KEY (BookingID) REFERENCES TIME_SLOT(BookingID) ON DELETE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE EVENT_TOPICS (
            BookingID INT NOT NULL,
            Topic VARCHAR(255) NOT NULL,
            PRIMARY KEY (BookingID, Topic),
            FOREIGN KEY (BookingID) REFERENCES TIME_SLOT(BookingID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE NOTIFICATIONS (
            NotificationID INT PRIMARY KEY AUTO_INCREMENT,
            BookingID INT,
            Title VARCHAR(255) DEFAULT NULL,
            Message TEXT DEFAULT NULL,
            Type ENUM('booking_approved', 'booking_cancelled', 'club_event', 'university_event', 'points_confirmation'),
            FOREIGN KEY (BookingID) REFERENCES TIME_SLOT(BookingID) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """)

        cursor.execute("""
        CREATE TABLE NOTIFICATION_PREFS (
            StudentID INT,
            ClubID INT,
            WantsClubNotifications BOOLEAN NOT NULL DEFAULT TRUE,
            WantsUniversityNotifications BOOLEAN NOT NULL DEFAULT TRUE,
            PRIMARY KEY (StudentID, ClubID),
            FOREIGN KEY (StudentID) REFERENCES STUDENT(ID) ON DELETE CASCADE,
            FOREIGN KEY (ClubID) REFERENCES CLUB(ID) ON DELETE CASCADE
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
            FOREIGN KEY (ClubID) REFERENCES Club(ID)
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

