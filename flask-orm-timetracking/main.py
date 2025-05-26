from flask import Flask, jsonify, render_template, request, make_response, redirect
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token, create_refresh_token, get_jwt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Configuration
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "my-super-secret-key-de-mns")  # Better to use environment variable
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///timetrack.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)  # Access token expires after 1 hour
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)  # Refresh token expires after 30 days
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]  # Look for tokens in cookies
app.config["JWT_COOKIE_CSRF_PROTECT"] = False     # Disable CSRF protection for cookies
app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production
app.config["JWT_COOKIE_SAMESITE"] = "Lax"  # Helps prevent CSRF

# Initialize extensions
jwt = JWTManager(app)
db = SQLAlchemy(app)

# Token blocklist for logout/revocation
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Callback to check if a token is revoked
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None

# Helper function to create and store JWT tokens
# In the create_and_store_token function (around line 45)
def create_and_store_token(username):
    # Create the JWT tokens
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    
    # Create a response object (will be used to set cookies)
    response = make_response(jsonify({"logged_in": True}))
    
    # Set the access token as an HTTP-only cookie
    response.set_cookie(
        'access_token_cookie',
        access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        max_age=3600,  # 1 hour in seconds
        samesite='Lax',
        path='/'  # Ensure cookie is available on all paths
    )
    
    # Set the refresh token as an HTTP-only cookie with longer expiration
    response.set_cookie(
        'refresh_token_cookie',
        refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        max_age=2592000,  # 30 days in seconds
        samesite='Lax',
        path='/'  # Ensure cookie is available on all paths
    )
    
    # Set a non-httpOnly cookie with minimal user info for frontend awareness
    response.set_cookie(
        'user_session',
        'active',  # Don't include sensitive data here
        httponly=False,
        secure=False,  # Set to True in production
        max_age=2592000,  # 30 days in seconds
        samesite='Lax',
        path='/'  # Ensure cookie is available on all paths
    )
    
    return access_token, refresh_token, response

# Helper function to get the JWT token from various sources
def get_token_from_request():
    """
    Extract the JWT token from the request
    
    Checks in this order:
    1. Authorization header (Bearer token)
    2. access_token_cookie
    3. Query parameter 'token'
    
    Returns:
        str or None: The JWT token if found, None otherwise
    """
    # Check Authorization header first (Bearer token)
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]  # Extract the token part
    
    # Check for token in cookies
    token = request.cookies.get('access_token_cookie')
    if token:
        return token
    
    # Check for token in query parameters (less secure, but sometimes needed)
    token = request.args.get('token')
    if token:
        return token
    
    return None

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    sessions = db.relationship('Session', backref='activity_rel', lazy=True)
    
    def __repr__(self):
        return f'<Activity {self.name}>'
    
    def to_dict(self):
        return self.name

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    
    def __repr__(self):
        return f'<Session {self.id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "activity": self.activity_rel.name,
            "duration": self.duration,
            "date": self.date.isoformat()
        }

# Routes
@app.route('/')
def index():
    # Check for token in cookies
    token = request.cookies.get('access_token_cookie')
    if not token:
        return redirect('/login')
    
    # Try to verify the token
    try:
        from flask_jwt_extended import decode_token
        decode_token(token)
        return render_template('index.html')
    except Exception:
        # If token is invalid, redirect to login
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    user = User.query.filter_by(username=username).first()
    
    # For simplicity, we're not hashing passwords here
    # In a real app, you should use a proper password hashing mechanism
    if user and user.password == password:
        # Create tokens and get response with cookies
        _, _, response = create_and_store_token(username)
        return response
    
    return jsonify({"msg": "Identifiants invalides", "logged_in": False}), 401

@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Endpoint to refresh the access token using a valid refresh token
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    
    response = make_response(jsonify({"msg": "Token refreshed successfully"}))
    response.set_cookie(
        'access_token_cookie',
        access_token,
        httponly=True,
        secure=False,  # Set to True in production
        max_age=3600,  # 1 hour
        samesite='Lax',
        path='/'  # Ensure cookie is available on all paths
    )
    
    # Also refresh the user_session cookie to keep it in sync
    response.set_cookie(
        'user_session',
        'active',
        httponly=False,
        secure=False,  # Set to True in production
        max_age=2592000,  # 30 days
        samesite='Lax',
        path='/'
    )
    
    return response

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """
    Endpoint to logout a user by revoking their tokens
    """
    jti = get_jwt()["jti"]
    now = datetime.utcnow()
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    
    response = make_response(jsonify({"msg": "Successfully logged out"}))
    
    # Clear all cookies with path specified
    response.delete_cookie('access_token_cookie', path='/')
    response.delete_cookie('refresh_token_cookie', path='/')
    response.delete_cookie('user_session', path='/')
    
    return response

@app.route('/api/me', methods=['GET'])
@jwt_required()
def me():
    current_user = get_jwt_identity()
    return jsonify(username=current_user), 200

@app.route('/api/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404
    
    sessions = Session.query.filter_by(user_id=user.id).all()
    return jsonify([session.to_dict() for session in sessions])

@app.route('/api/sessions', methods=['POST'])
@jwt_required()
def add_session():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404
    
    data = request.json
    activity_name = data.get("activity")
    duration = data.get("duration")
    
    # Validate data
    if not activity_name or not duration:
        return jsonify({"msg": "Données manquantes"}), 400
    
    try:
        duration = int(duration)
    except ValueError:
        return jsonify({"msg": "La durée doit être un nombre"}), 400
    
    # Get or create activity
    activity = Activity.query.filter_by(name=activity_name).first()
    if not activity:
        activity = Activity(name=activity_name)
        db.session.add(activity)
        db.session.commit()
    
    # Create session
    session = Session(
        duration=duration,
        user_id=user.id,
        activity_id=activity.id,
        date=datetime.now(datetime.UTC)
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({"message": "Session enregistrée", "session": session.to_dict()}), 201

@app.route('/api/activities', methods=['GET'])
@jwt_required()
def get_activities():
    activities = Activity.query.all()
    return jsonify([activity.to_dict() for activity in activities])

@app.route('/api/activities', methods=['POST'])
@jwt_required()
def add_activity():
    data = request.json
    name = data.get("name")
    
    if not name:
        return jsonify({"msg": "Nom d'activité manquant"}), 400
    
    # Check if activity already exists
    existing = Activity.query.filter_by(name=name).first()
    if existing:
        return jsonify({"message": "Cette activité existe déjà", "activity": name}), 400
    
    activity = Activity(name=name)
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({"message": "Activité ajoutée", "activity": name}), 201

@app.route('/api/activities/<string:name>', methods=['DELETE'])
@jwt_required()
def delete_activity(name):
    # Find the activity
    activity = Activity.query.filter_by(name=name).first()
    
    if not activity:
        return jsonify({"message": "Activité non trouvée"}), 404
    
    # Check if the activity is used in any sessions
    sessions = Session.query.filter_by(activity_id=activity.id).all()
    if sessions:
        return jsonify({
            "message": "Impossible de supprimer cette activité car elle est utilisée dans des sessions",
            "sessions_count": len(sessions)
        }), 400
    
    # Delete the activity
    db.session.delete(activity)
    db.session.commit()
    
    return jsonify({"message": "Activité supprimée avec succès"}), 200

# Initialize database and create default user
with app.app_context():
    db.create_all()
    
    # Add default user if not exists
    if not User.query.filter_by(username="mns").first():
        default_user = User(username="mns", password="mns")
        db.session.add(default_user)
        
        # Add default activities
        default_activities = ["lecture", "sport", "travail"]
        for activity_name in default_activities:
            if not Activity.query.filter_by(name=activity_name).first():
                activity = Activity(name=activity_name)
                db.session.add(activity)
        
        db.session.commit()

# Configure JWT to use our custom token loader
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    # You could implement token blacklisting here
    # For now, we'll just return False (no tokens are blacklisted)
    return False

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(username=identity).one_or_none()

# Add a route to check authentication status
@app.route('/api/auth-status', methods=['GET'])
def auth_status():
    token = get_token_from_request()
    if not token:
        return jsonify({"authenticated": False}), 401
    
    try:
        # Verify the token is valid
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        username = decoded.get('sub')
        
        return jsonify({
            "authenticated": True,
            "username": username
        })
    except Exception as e:
        return jsonify({"authenticated": False, "error": str(e)}), 401

# Add a logout route
@app.route('/logout', methods=['POST'])
def logout():
    response = make_response(jsonify({"message": "Déconnecté avec succès"}))
    response.delete_cookie('access_token_cookie')
    return response


@app.route('/api/activities', methods=['POST'])
@jwt_required()
def create_activity():  # Changed from add_activity to create_activity
    data = request.json
    name = data.get("name")
    
    if not name:
        return jsonify({"msg": "Nom d'activité manquant"}), 400
    
    # Check if activity already exists
    existing = Activity.query.filter_by(name=name).first()
    if existing:
        return jsonify({"message": "Cette activité existe déjà", "activity": name}), 400
    
    activity = Activity(name=name)
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({"message": "Activité ajoutée", "activity": name}), 201

@app.after_request
def add_header(response):
    # Prevent caching of scripts during development
    if request.path.startswith('/static/js/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)
