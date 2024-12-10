import sqlite3

def view_tables(db_path):
    """
    Prints records from Flasche and Rezept_besteht_aus_Granulat tables separately.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # View Flasche table
        print("\n=== Flasche Table ===")
        cursor.execute("SELECT * FROM Flasche")
        rows = cursor.fetchall()
        
        print("Flaschen_ID | Rezept_ID | Tagged_Date | has_error")
        print("-" * 50)
        for row in rows:
            print(f"{row[0]:<11} | {row[1]:<9} | {row[2]:<11} | {row[3]}")

        # View Rezept_besteht_aus_Granulat table
        print("\n=== Rezept_besteht_aus_Granulat Table ===")
        cursor.execute("SELECT * FROM Rezept_besteht_aus_Granulat")
        rows = cursor.fetchall()
        
        print("Rezept_ID | Granulat_ID | Menge")
        print("-" * 40)
        for row in rows:
            print(f"{row[0]:<9} | {row[1]:<11} | {row[2]}")
    
    except sqlite3.Error as e:
        print(f"Error viewing database: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    DB_PATH = "/home/maxsim/maxsim-NFC-raspi/data/flaschen_database.db"
    view_tables(DB_PATH)