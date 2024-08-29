import sqlite3

def create_table():
    conn = sqlite3.connect('referral_bot.db')
    c = conn.cursor()
    
    # Check if the database is not corrupted
    try:
        c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            referred_by INTEGER,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
    except sqlite3.DatabaseError as e:
        print(f"Database Error: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    create_table()
