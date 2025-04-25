
# RoomQuest Backend

RoomQuest is a web-based platform that helps students, clubs, and administrators at the University of Calgary find, book, and manage study spaces, classrooms, and campus events. This repository contains the **Flask-based backend** of the project, which handles all API routing, database transactions, and authentication.

## Project Structure

```
backend/
├── app.py                      # Main Flask app
├── config.py                   # MySQL database connection setup
├── routes/
│   ├── auth.py                 # Login/authentication
│   ├── events.py               # Event creation and lookup
│   ├── features_add_del.py     # Feature management
│   ├── init_db_route.py        # Database reset/init
│   ├── notifications.py        # Notification handling
│   ├── points.py               # Leaderboard and points
│   ├── profile.py              # Profile info
│   ├── reservUpcoming.py       # Reservation summaries
│   ├── rooms.py                # Room search API
│   ├── seed_data.py            # Dummy data seeding
│   ├── signup_db.py            # Signup endpoints
│   ├── test_connection_route.py # Connection check
│   └── user_list_bp.py         # List all users
└── services/
    └── scheduler.py            # Time-slot overlap checks
    └── admin.py                # Admin endpoints
---
```

## Tech Stack

- **Python 3.10+**
- **Flask** (API framework)
- **MySQL** (Database)
- **Azure** (Hosting for MySQL)
- **Flask-CORS** for frontend-backend communication


## Setup Instructions

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/roomquest-backend.git
   cd roomquest-backend
   ```

2. **Create virtual environment & activate it**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up `.env` or environmental variables manually**  
   You will need:
   - `DB_HOST`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`

5. **Run the Flask server**
   ```bash
   python app.py
   ```
---

## Core Features

- Room and feature search
- Booking requests with admin approval
- Event creation and filtering
- Custom notifications
- User types: students, clubs, admins
- Real-time data from Azure-hosted MySQL
- Clean separation between routes and logic

---

## Development Notes

- All API routes are prefixed with `/api/`
- Ensure the database is initialized using `/init-db` before running
- CORS is enabled for cross-origin requests from the Wix front end

---

## Contributors

- Yash D
- Devanshi I
- Kevlam C

