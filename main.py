from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import base64
from io import BytesIO
from PIL import Image
import datetime
import read_plate
import os
from werkzeug.utils import secure_filename
import shutil
# from flask import current_app as app

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = 'static/uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db_connection():
    conn = sqlite3.connect('vehicles.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('scan'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("regitering")
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                         (username, email, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                            (email, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('scan'))
        else:
            flash('Incorrect email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        vehicle_image = request.files['vehicle_image']
        
        if vehicle_image and allowed_file(vehicle_image.filename):
            filename = secure_filename(vehicle_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            vehicle_image.save(image_path)
            
            # Placeholder for number plate recognition logic
            number_plate = read_plate.read_number(image_path)
            print(number_plate)
            
            conn = get_db_connection()
            vehicle = conn.execute('SELECT * FROM vehicles WHERE vehicle_number = ?', 
                                   (number_plate,)).fetchone()
            if vehicle:
                conn.execute('INSERT INTO records (vehicle_id, old_owner_name, timestamp) VALUES (?, ?, CURRENT_TIMESTAMP)', 
                         (vehicle['id'], vehicle['owner_name']))
                conn.commit()
                conn.close()
                flash('Vehicle found and record added.', 'success')
                return redirect(url_for('records'))
            else:
                conn.close()
                flash('Vehicle not found. Please register the vehicle.', 'warning')
                return render_template('vehicle_register.html',vehicle_number=number_plate,vehicle_image=vehicle_image)
                # return redirect(url_for('vehicle_register' ,scanned_number=number_plate))
        else:
            flash('Invalid file type.', 'danger')
            return redirect(url_for('scan'))
    
    return render_template('scan.html')

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/scan', methods=['GET', 'POST'])
# def scan():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     if request.method == 'POST':
#         vehicle_image = request.files['vehicle_image']
#         image_data = vehicle_image
        
#         # Placeholder for number plate recognition logic
#         number_plate = read_plate.read_number(vehicle_image) # Replace this with actual logic
        
#         conn = get_db_connection()
#         vehicle = conn.execute('SELECT * FROM vehicles WHERE vehicle_number = ?', 
#                                (number_plate,)).fetchone()
#         if vehicle:
#             conn.execute('INSERT INTO records (vehicle_id, old_owner_name) VALUES (?, ?)', 
#                          (vehicle['id'], vehicle['owner_name']))
#             conn.commit()
#             flash('Vehicle found and record added.', 'success')
#             return redirect(url_for('records'))
#         else:
#             conn.close()
#             flash('Vehicle not found. Please register the vehicle.', 'warning')
#             return redirect(url_for('vehicle_register'))
#     return render_template('scan.html')

@app.route('/vehicle_register', methods=['GET', 'POST'])
def vehicle_register():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        vehicle_number = request.form['vehicle_number']
        vehicle_image = request.files['vehicle_image']
        image_data = vehicle_image.read()
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO vehicles (owner_name, vehicle_number, vehicle_image) VALUES (?, ?, ?)', 
                         (owner_name, vehicle_number, image_data))
            conn.commit()
            flash('Vehicle registered successfully!', 'success')
            return redirect(url_for('scan'))
        except sqlite3.IntegrityError:
            flash('Vehicle number already exists.', 'error')
        finally:
            conn.close()
    
    return render_template('vehicle_register.html')



@app.route('/records')
def records():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    records = conn.execute('''
        SELECT owner_name, vehicle_number, vehicle_image, timestamp
        FROM vehicles
        ORDER BY owner_name DESC
    ''').fetchall()
    conn.close()
    print("Records",records)

    
    # Process image data for display
    processed_records = []
    for record in records:
        processed_record = dict(record)
        if record['vehicle_image']:
            processed_record['vehicle_image'] = base64.b64encode(record['vehicle_image']).decode('utf-8')
        else:
            processed_record['vehicle_image'] = None
        processed_records.append(processed_record)
    
    return render_template('records.html', records=processed_records)

# @app.route('/records')
# def records():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     conn = get_db_connection()
#     records = conn.execute('''
#         SELECT v.vehicle_number, v.owner_name, v.vehicle_image, r.timestamp 
#         FROM records r 
#         JOIN vehicles v ON r.vehicle_id = v.id
#         ORDER BY r.timestamp DESC
#     ''').fetchall()
#     conn.close()
    
#     for record in records:
#         if record['vehicle_image']:
#             record['vehicle_image'] = base64.b64encode(record['vehicle_image']).decode('utf-8')
    
#     return render_template('records.html', records=records)

@app.route('/new_user', methods=['GET', 'POST'])
def new_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', 
                         (username, email, password))
            conn.commit()
            flash('New user created successfully!', 'success')
            return redirect(url_for('new_user'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.', 'error')
        finally:
            conn.close()
    
    return render_template('new_user.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
