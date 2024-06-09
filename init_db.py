import sqlite3

def init_db():
    conn = sqlite3.connect('vehicles.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    
    # Create vehicles table
    c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT NOT NULL,
        vehicle_number TEXT NOT NULL UNIQUE,
        vehicle_image BLOB,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create records table
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        old_owner_name TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
    )''')
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
