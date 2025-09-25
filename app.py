from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Set timezone for Indian Standard Time
indian_timezone = pytz.timezone('Asia/Kolkata')

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(1), default='A')  # A-Available, O-Occupied
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=True)
    total_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Function to calculate parking duration
def calculate_parking_duration(start_time, end_time=None):
    """Calculate the duration between two timestamps"""
    if end_time is None:
        end_time = datetime.now(indian_timezone)
    
    # Convert naive datetimes to timezone-aware (assume Indian timezone if naive)
    if start_time.tzinfo is None:
        # If it's a naive datetime, assume it's in Indian timezone
        start_time = indian_timezone.localize(start_time)
    if end_time.tzinfo is None:
        # If it's a naive datetime, assume it's in Indian timezone
        end_time = indian_timezone.localize(end_time)
    
    duration = end_time - start_time
    total_seconds = duration.total_seconds()
    
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    return {
        'hours': hours,
        'minutes': minutes,
        'total_seconds': total_seconds,
        'total_hours': total_seconds / 3600
    }

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('This username is already taken! Please choose a different one.', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('This email is already registered! Please use a different email.', 'error')
            return redirect(url_for('register'))
        
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now login with your credentials.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# User and Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # First check if it's an admin login
        admin_user = Admin.query.filter_by(username=username).first()
        if admin_user and check_password_hash(admin_user.password_hash, password):
            session['admin_id'] = admin_user.id
            session['admin_username'] = admin_user.username
            flash('Welcome back, Administrator!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # If not admin, check if it's a regular user
        regular_user = User.query.filter_by(username=username).first()
        if regular_user and check_password_hash(regular_user.password_hash, password):
            session['user_id'] = regular_user.id
            session['username'] = regular_user.username
            flash('Welcome back! You have successfully logged in.', 'success')
            return redirect(url_for('user_dashboard'))
        
        # If neither admin nor user, show error
        flash('Invalid username or password. Please try again.', 'error')
    
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out. Come back soon!', 'success')
    return redirect(url_for('index'))

# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        flash('Please login as an administrator to access this page!', 'error')
        return redirect(url_for('login'))
    
    all_parking_lots = ParkingLot.query.all()
    all_users = User.query.all()
    total_parking_spots = db.session.query(ParkingSpot).count()
    currently_occupied_spots = db.session.query(ParkingSpot).filter_by(status='O').count()
    currently_available_spots = total_parking_spots - currently_occupied_spots
    
    return render_template('admin_dashboard.html', 
                         parking_lots=all_parking_lots, 
                         users=all_users,
                         total_spots=total_parking_spots,
                         occupied_spots=currently_occupied_spots,
                         available_spots=currently_available_spots)

# Manage Parking Lots
@app.route('/admin/parking_lots', methods=['GET', 'POST'])
def manage_parking():
    if 'admin_id' not in session:
        flash('Please login as an administrator to access this page!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location_name = request.form['location_name']
        hourly_rate = float(request.form['hourly_rate'])
        address = request.form['address']
        pin_code = request.form['pin_code']
        total_spots = int(request.form['total_spots'])
        
        new_parking_lot = ParkingLot(
            location_name=location_name,
            hourly_rate=hourly_rate,
            address=address,
            pin_code=pin_code,
            total_spots=total_spots
        )
        db.session.add(new_parking_lot)
        db.session.commit()
        
        # Create individual parking spots for this lot
        for spot_number in range(1, total_spots + 1):
            new_spot = ParkingSpot(
                lot_id=new_parking_lot.id,
                spot_number=spot_number,
                status='A'
            )
            db.session.add(new_spot)
        
        db.session.commit()
        flash('New parking lot has been created successfully!', 'success')
        return redirect(url_for('manage_parking'))
    
    all_parking_lots = ParkingLot.query.all()
    return render_template('manage_parking.html', parking_lots=all_parking_lots)

# Edit Parking Lot
@app.route('/admin/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(lot_id):
    if 'admin_id' not in session:
        flash('Please login as an administrator to access this page!', 'error')
        return redirect(url_for('login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    if request.method == 'POST':
        # Check if any spots are currently occupied
        occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
        if occupied_spots_count > 0:
            flash('Cannot edit parking lot while spots are occupied! Please wait for all spots to be vacated.', 'error')
            return redirect(url_for('manage_parking'))
        
        new_total_spots = int(request.form['total_spots'])
        current_spots_count = ParkingSpot.query.filter_by(lot_id=lot_id).count()
        
        parking_lot.location_name = request.form['location_name']
        parking_lot.hourly_rate = float(request.form['hourly_rate'])
        parking_lot.address = request.form['address']
        parking_lot.pin_code = request.form['pin_code']
        parking_lot.total_spots = new_total_spots
        
        # Add or remove spots as needed
        if new_total_spots > current_spots_count:
            for spot_number in range(current_spots_count + 1, new_total_spots + 1):
                new_spot = ParkingSpot(lot_id=lot_id, spot_number=spot_number, status='A')
                db.session.add(new_spot)
        elif new_total_spots < current_spots_count:
            spots_to_remove = ParkingSpot.query.filter_by(lot_id=lot_id).limit(current_spots_count - new_total_spots).all()
            for spot in spots_to_remove:
                db.session.delete(spot)
        
        db.session.commit()
        flash('Parking lot information has been updated successfully!', 'success')
        return redirect(url_for('manage_parking'))
    
    return render_template('edit_parking.html', parking_lot=parking_lot)

# Delete Parking Lot
@app.route('/admin/delete_parking_lot/<int:lot_id>')
def delete_parking_lot(lot_id):
    if 'admin_id' not in session:
        flash('Please login as an administrator to access this page!', 'error')
        return redirect(url_for('login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    
    # Check if any spots are currently occupied
    occupied_spots_count = ParkingSpot.query.filter_by(lot_id=lot_id, status='O').count()
    if occupied_spots_count > 0:
        flash('Cannot delete parking lot while spots are occupied! Please wait for all spots to be vacated.', 'error')
        return redirect(url_for('manage_parking'))
    
    db.session.delete(parking_lot)
    db.session.commit()
    flash('Parking lot has been deleted successfully!', 'success')
    return redirect(url_for('manage_parking'))

@app.route('/admin/parking_spots/<int:lot_id>')
def admin_parking_spots(lot_id):
    if 'admin_id' not in session:
        flash('Please login as an administrator to access this page!', 'error')
        return redirect(url_for('login'))
    
    parking_lot = ParkingLot.query.get_or_404(lot_id)
    all_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    
    # Get reservation details for occupied spots
    spots_with_details = []
    for spot in all_spots:
        if spot.status == 'O':
            current_reservation = Reservation.query.filter_by(spot_id=spot.id, status='active').first()
            if current_reservation:
                # Calculate duration for occupied spots
                duration_info = calculate_parking_duration(current_reservation.entry_time)
                current_reservation.duration_hours = duration_info['hours']
                current_reservation.duration_minutes = duration_info['minutes']
            spots_with_details.append({
                'spot': spot,
                'reservation': current_reservation
            })
        else:
            spots_with_details.append({
                'spot': spot,
                'reservation': None
            })
    
    return render_template('parking-spots.html', 
                         parking_lot=parking_lot, 
                         spot_details=spots_with_details)

# User Dashboard
@app.route('/user/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        flash('Please login to access your dashboard!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    current_reservations = Reservation.query.filter_by(user_id=user_id, status='active').all()
    past_reservations = Reservation.query.filter_by(user_id=user_id, status='completed').limit(10).all()
    
    # Calculate durations for current reservations
    for reservation in current_reservations:
        duration_info = calculate_parking_duration(reservation.entry_time)
        reservation.duration_hours = duration_info['hours']
        reservation.duration_minutes = duration_info['minutes']
        reservation.current_cost = duration_info['total_hours'] * reservation.parking_spot.parking_lot.hourly_rate
    
    # Calculate total parking time and cost
    total_parking_hours = 0
    total_parking_cost = 0
    for reservation in past_reservations:
        if reservation.exit_time:
            duration_info = calculate_parking_duration(reservation.entry_time, reservation.exit_time)
            reservation.duration_hours = duration_info['hours']
            reservation.duration_minutes = duration_info['minutes']
            total_parking_hours += duration_info['total_hours']
            total_parking_cost += reservation.total_cost
        else:
            reservation.duration_hours = 0
            reservation.duration_minutes = 0
    
    return render_template('user_dashboard.html',
                         active_reservations=current_reservations,
                         completed_reservations=past_reservations,
                         total_parking_time=round(total_parking_hours, 2),
                         total_cost=round(total_parking_cost, 2))

# Book Parking
@app.route('/user/book_parking')
def book_parking():
    if 'user_id' not in session:
        flash('Please login to book parking!', 'error')
        return redirect(url_for('login'))
    
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # Case-insensitive search on location name, address, or pin code
        matching_lots = ParkingLot.query.filter(
            (ParkingLot.location_name.ilike(f'%{search_query}%')) |
            (ParkingLot.address.ilike(f'%{search_query}%')) |
            (ParkingLot.pin_code.ilike(f'%{search_query}%'))
        ).all()
    else:
        matching_lots = ParkingLot.query.all()
    
    lots_with_availability = []
    for lot in matching_lots:
        available_spots_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
        if available_spots_count > 0:
            lots_with_availability.append({
                'lot': lot,
                'available_spots': available_spots_count
            })
    
    return render_template('book_parking.html', available_lots=lots_with_availability)

@app.route('/user/book_spot/<int:lot_id>')
def book_spot(lot_id):
    if 'user_id' not in session:
        flash('Please login to book parking!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    # Check if user already has an active reservation
    existing_reservation = Reservation.query.filter_by(user_id=user_id, status='active').first()
    if existing_reservation:
        flash('You already have an active parking reservation! Please release your current spot first.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Find available spot
    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
    if not available_spot:
        flash('Sorry, no available spots in this parking lot at the moment!', 'error')
        return redirect(url_for('book_parking'))
    
    # Create new reservation
    new_reservation = Reservation(
        spot_id=available_spot.id,
        user_id=user_id,
        entry_time=datetime.now(indian_timezone),
        status='active'
    )
    
    # Update spot status to occupied
    available_spot.status = 'O'
    
    db.session.add(new_reservation)
    db.session.commit()
    
    flash('Congratulations! Your parking spot has been booked successfully!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/user/release_spot/<int:reservation_id>')
def release_spot(reservation_id):
    if 'user_id' not in session:
        flash('Please login to manage your parking!', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=user_id, status='active').first()
    
    if not reservation:
        flash('Reservation not found! Please check your dashboard.', 'error')
        return redirect(url_for('user_dashboard'))
    
    # Calculate cost using the calculate_parking_duration function
    exit_time = datetime.now(indian_timezone)
    duration_info = calculate_parking_duration(reservation.entry_time, exit_time)
    final_cost = duration_info['total_hours'] * reservation.parking_spot.parking_lot.hourly_rate
    
    # Update reservation
    reservation.exit_time = exit_time
    reservation.total_cost = final_cost
    reservation.status = 'completed'
    
    # Update spot status to available
    reservation.parking_spot.status = 'A'
    
    db.session.commit()
    
    flash(f'Spot released successfully! Your total parking cost is: ${final_cost:.2f}', 'success')
    return redirect(url_for('user_dashboard'))

# Parking Statistics API
@app.route('/api/parking_stats')
def parking_stats():
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    
    total_parking_spots = db.session.query(ParkingSpot).count()
    currently_occupied_spots = db.session.query(ParkingSpot).filter_by(status='O').count()
    currently_available_spots = total_parking_spots - currently_occupied_spots
    
    # Get parking lot statistics
    all_lots = ParkingLot.query.all()
    lot_statistics = []
    for lot in all_lots:
        lot_total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        lot_occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
        lot_statistics.append({
            'name': lot.location_name,
            'total': lot_total_spots,
            'occupied': lot_occupied_spots,
            'available': lot_total_spots - lot_occupied_spots
        })
    
    return jsonify({
        'total_spots': total_parking_spots,
        'occupied_spots': currently_occupied_spots,
        'available_spots': currently_available_spots,
        'lot_stats': lot_statistics
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default administrator if not exists
        default_admin = Admin.query.filter_by(username='admin').first()
        if not default_admin:
            default_admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Default administrator account created - Username: admin, Password: admin123")
    
    app.run(debug=True) 