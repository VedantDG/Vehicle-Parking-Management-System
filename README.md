# Vehicle Parking Management System

A comprehensive web-based parking management application built with Flask that allows users to book parking spots and administrators to manage parking lots efficiently.

## Features

### User Features
- User registration and authentication
- Search and book available parking spots
- Real-time parking spot availability
- View current and past parking reservations
- Automatic cost calculation based on parking duration
- Release parking spots when leaving

### Administrator Features
- Admin dashboard with comprehensive statistics
- Create, edit, and delete parking lots
- Manage parking spots for each lot
- View real-time occupancy status
- Monitor all user reservations
- Track parking lot performance

### System Features
- Real-time parking spot status updates
- Automatic cost calculation using hourly rates
- Timezone-aware timestamps (Indian Standard Time)
- Secure password hashing
- Responsive web interface with Bootstrap
- SQLite database for data persistence

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Authentication**: Werkzeug password hashing
- **Timezone**: pytz for Indian Standard Time support

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "V1 - Vehicle Parking App"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your web browser and navigate to `http://localhost:5000`

## Default Credentials

### Administrator Account
- **Username**: `admin`
- **Password**: `admin123`

**Note**: Change the default admin password in production environments for security.

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Admins Table
- `id`: Primary key
- `username`: Unique admin username
- `password_hash`: Hashed password
- `created_at`: Account creation timestamp

### Parking Lots Table
- `id`: Primary key
- `location_name`: Name of the parking location
- `hourly_rate`: Cost per hour for parking
- `address`: Full address of the parking lot
- `pin_code`: Postal code of the location
- `total_spots`: Maximum number of vehicles the lot can accommodate
- `created_at`: Record creation timestamp

### Parking Spots Table
- `id`: Primary key
- `lot_id`: Foreign key referencing parking lot
- `spot_number`: Individual spot number within the lot
- `status`: Spot status (A=Available, O=Occupied)
- `created_at`: Record creation timestamp

### Reservations Table
- `id`: Primary key
- `spot_id`: Foreign key referencing parking spot
- `user_id`: Foreign key referencing user
- `entry_time`: Vehicle entry timestamp
- `exit_time`: Vehicle exit timestamp (null for active reservations)
- `total_cost`: Total parking cost
- `status`: Reservation status (active, completed, cancelled)
- `created_at`: Reservation creation timestamp

## Usage Guide

### For Users

1. **Registration**: Create a new account with username, email, and password
2. **Login**: Access your account using your credentials
3. **Book Parking**: 
   - Search for parking lots by location, address, or pin code
   - Select an available parking lot
   - Book an available spot
4. **Manage Reservations**: 
   - View current active reservations
   - Check parking duration and current cost
   - Release spot when leaving
5. **View History**: Access past parking reservations and total costs

### For Administrators

1. **Login**: Use admin credentials to access the admin dashboard
2. **Manage Parking Lots**:
   - Create new parking lots with location details and hourly rates
   - Edit existing parking lot information
   - Delete parking lots (only when no spots are occupied)
3. **Monitor Spots**: View real-time status of all parking spots
4. **View Statistics**: Access comprehensive parking statistics and user data

## API Endpoints

### Public Endpoints
- `GET /`: Home page
- `GET /register`: User registration page
- `POST /register`: Process user registration
- `GET /login`: Login page
- `POST /login`: Process login (users and admins)
- `GET /logout`: Logout and clear session

### User Endpoints (Requires user authentication)
- `GET /user/dashboard`: User dashboard
- `GET /user/book_parking`: Search and book parking
- `GET /user/book_spot/<lot_id>`: Book specific spot
- `GET /user/release_spot/<reservation_id>`: Release parking spot

### Admin Endpoints (Requires admin authentication)
- `GET /admin/dashboard`: Admin dashboard
- `GET /admin/parking_lots`: Manage parking lots page
- `POST /admin/parking_lots`: Create new parking lot
- `GET /admin/edit_parking_lot/<lot_id>`: Edit parking lot page
- `POST /admin/edit_parking_lot/<lot_id>`: Update parking lot
- `GET /admin/delete_parking_lot/<lot_id>`: Delete parking lot
- `GET /admin/parking_spots/<lot_id>`: View parking spots for a lot
- `GET /api/parking_stats`: Get parking statistics (JSON)

## Configuration

### Environment Variables
The application uses the following configuration:
- `SECRET_KEY`: Flask secret key for session management
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `SQLALCHEMY_TRACK_MODIFICATIONS`: SQLAlchemy modification tracking

### Timezone Configuration
The application is configured for Indian Standard Time (Asia/Kolkata) using the pytz library.

## File Structure

```
V1 - Vehicle Parking App/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── instance/
│   └── parking.db        # SQLite database file
├── static/
│   └── images/
│       └── background.png # Background image
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── user_dashboard.html # User dashboard
│   ├── admin_dashboard.html # Admin dashboard
│   ├── book_parking.html # Parking booking page
│   ├── manage_parking.html # Parking management page
│   ├── edit_parking.html # Edit parking lot page
│   └── parking-spots.html # Parking spots view
└── venv/                 # Virtual environment
```

## Security Features

- Password hashing using Werkzeug's secure password hashing
- Session-based authentication
- Input validation and sanitization
- SQL injection prevention through SQLAlchemy ORM
- Admin-only access to sensitive operations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support and questions, please open an issue in the repository or contact the development team.

## Future Enhancements

- Payment integration for online payments
- Mobile application development
- Advanced reporting and analytics
- Multi-language support
- Email notifications for reservations
- QR code generation for parking spots
- Integration with GPS for location-based services