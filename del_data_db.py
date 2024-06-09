import sqlite3

def init_db():
    conn = sqlite3.connect('vehicles.db')
    c = conn.cursor()
    

    c.execute('''DELETE FROM vehicles WHERE id=6;
    ''')

    conn.commit()
    conn.close()

init_db()