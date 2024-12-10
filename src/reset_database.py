import sqlite3

def reset_database(db_path):
    """
    Resets the Flasche table in the database by clearing the Tagged_Date
    and setting has_error to 0.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Reset the Flasche table
        cursor.execute('''
            UPDATE Flasche
            SET Tagged_Date = 0, has_error = 0
        ''')
        conn.commit()
        print("Database reset successfully!")
    
    except sqlite3.Error as e:
        print(f"Error resetting database: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Provide the path to your database file
    DB_PATH = "/home/maxsim/maxsim-NFC-raspi/data/flaschen_database.db"
    reset_database(DB_PATH)
