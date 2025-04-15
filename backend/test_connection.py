from config import get_connection

try:
    conn = get_connection()
    if conn.is_connected():
        print("✅ Successfully connected to the database!")
    else:
        print("❌ Connection failed.")
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
