from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # Import CORS for cross-origin requests
from sqlalchemy import text
from utils.encryption import encrypt_data, decrypt_data
from datetime import datetime, timedelta
from utils.biometric import verify_face
from utils.password_generator import generate_password
from utils.mfa import generate_secret_key, generate_otp, verify_otp, get_qr_code_url
import bcrypt, jwt, os
import base64
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure database and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///password_manager.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 30}  # Add timeout for database connections
}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-default-secret-key-for-testing')
db = SQLAlchemy(app)

# Dictionary to store OTP secrets temporarily (should use a more persistent solution in production)
otp_secrets = {}

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # User's full name
    email = db.Column(db.String(100), unique=True, nullable=False)  # User's email (unique)
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed master password
    phone_number = db.Column(db.String(15), nullable=False)  # User's phone number
    face_embedding = db.Column(db.LargeBinary, nullable=False)  # Encoded facial embedding
    otp_secret = db.Column(db.String(16), nullable=False)  # Secret key for OTP-based MFA

# Define PasswordEntry model
class PasswordEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user
    website_name = db.Column(db.String(100), nullable=False)  # Name of the website
    website_url = db.Column(db.String(200), nullable=False)  # URL of the website
    encrypted_password = db.Column(db.String(200), nullable=False)  # Encrypted password

# Define AuditLog model
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Link to the user
    action = db.Column(db.String(200), nullable=False)  # Description of the action
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp of the action

# Home route
@app.route('/')
def home():
    return "Welcome to the Password Manager Backend!"

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find the user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify the password - Fix the string/bytes handling
    if isinstance(user.password_hash, str):
        stored_hash = user.password_hash.encode('utf-8')
    else:
        stored_hash = user.password_hash
        
    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        return jsonify({"error": "Invalid password"}), 401
    # Generate JWT token
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
        app.config['SECRET_KEY'], algorithm='HS256'
    )
    
    # Log the login action
    log_entry = AuditLog(user_id=user.id, action=f"User logged in from {request.remote_addr}")
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"message": "Login successful", "token": token, "user_id": user.id}), 200

# Signup endpoint
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        face_embedding_base64 = data.get('face_embedding')

        # Validate input
        if not all([name, email, password, phone_number, face_embedding_base64]):
            missing_fields = []
            if not name: missing_fields.append("name")
            if not email: missing_fields.append("email")
            if not password: missing_fields.append("password")
            if not phone_number: missing_fields.append("phone_number")
            if not face_embedding_base64: missing_fields.append("face_embedding")
            
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409  # 409 Conflict

        # Decode base64 face embedding
        try:
            print(f"Processing face embedding for user: {email}")
            face_image_bytes = base64.b64decode(face_embedding_base64)
            
            # Process the face image to extract embedding
            import numpy as np
            import cv2
            from io import BytesIO
            from PIL import Image
            import pickle
            
            # Convert bytes to image
            img = Image.open(BytesIO(face_image_bytes))
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            
            # Load face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return jsonify({"error": "No face detected in the provided image"}), 400
            
            # Get the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Extract face ROI
            face_roi = img_cv[y:y+h, x:x+w]
            
            # Resize to a standard size
            face_roi = cv2.resize(face_roi, (128, 128))
            
            # Convert to grayscale and flatten for simple comparison
            face_roi_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            face_embedding = face_roi_gray.flatten().astype(np.float32)
            
            # Serialize the embedding
            face_embedding_bytes = pickle.dumps(face_embedding)
            
            print(f"Face embedding processed successfully for user: {email}")
            
        except ImportError as e:
            print(f"Import error during face processing: {str(e)}")
            return jsonify({"error": f"Server configuration error: {str(e)}. Please contact support."}), 500
        except Exception as e:
            print(f"Error processing face embedding: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Invalid face embedding format or processing error: {str(e)}"}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Generate OTP secret key
        otp_secret = generate_secret_key()

        # Create a new user with retry logic for database lock
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                new_user = User(
                    name=name,
                    email=email,
                    password_hash=hashed_password.decode('utf-8'),
                    phone_number=phone_number,
                    face_embedding=face_embedding_bytes,
                    otp_secret=otp_secret
                )
                db.session.add(new_user)
                db.session.commit()
                print(f"User created successfully: {email}")
                
                # Generate QR code URL for Google Authenticator
                qr_code_url = get_qr_code_url(otp_secret, email)
                
                # Log the signup action
                try:
                    log_entry = AuditLog(user_id=new_user.id, action=f"User registered from {request.remote_addr}")
                    db.session.add(log_entry)
                    db.session.commit()
                except Exception as e:
                    print(f"Error logging signup action: {str(e)}")
                    # Non-critical error, continue without failing
                
                return jsonify({
                    "message": "User registered successfully",
                    "qr_code_url": qr_code_url,
                    "secret_key": otp_secret
                }), 201
                
            except Exception as e:
                db.session.rollback()
                retry_count += 1
                
                if "database is locked" in str(e).lower():
                    print(f"Database locked, retrying ({retry_count}/{max_retries})...")
                    import time
                    time.sleep(1)  # Wait before retrying
                else:
                    print(f"Database error during user creation: {str(e)}")
                    return jsonify({"error": f"Database error: {str(e)}"}), 500
        
        # If we've exhausted all retries
        return jsonify({"error": "Database is currently busy. Please try again later."}), 503

    except Exception as e:
        # Log the error and return a generic response
        print(f"Unexpected error during signup: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "An unexpected error occurred during signup"}), 500

#Add email check endpoint
@app.route('/api/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter is required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    return jsonify({"exists": existing_user is not None}), 200
# Add password endpoint
@app.route('/api/add-password', methods=['POST'])
def add_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Parse request data
    data = request.json
    website_name = data.get('website_name')
    website_url = data.get('website_url')
    password = data.get('password')

    # Validate input
    if not all([website_name, website_url, password]):
        return jsonify({"error": "All fields are required"}), 400

    # Encrypt the password
    encrypted_password = encrypt_data(password)

    # Create a new password entry
    new_password_entry = PasswordEntry(
        user_id=user_id,
        website_name=website_name,
        website_url=website_url,
        encrypted_password=encrypted_password
    )
    db.session.add(new_password_entry)
    
    # Log the action
    log_entry = AuditLog(user_id=user_id, action=f"Added password for {website_name}")
    db.session.add(log_entry)
    
    db.session.commit()

    return jsonify({"message": "Password added successfully"}), 201

# Verify face endpoint
@app.route('/api/verify-face', methods=['POST'])
def verify_face_endpoint():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Parse captured face image from either file upload or base64 data
    if 'face_image' in request.files:
        # For multipart/form-data
        captured_image = request.files['face_image'].read()
    elif request.json and 'face_image' in request.json:
        # For JSON with base64 data
        try:
            captured_image = base64.b64decode(request.json['face_image'])
        except Exception as e:
            # Log the error
            log_entry = AuditLog(
                user_id=user_id, 
                action=f"Face verification failed: Invalid image format - {str(e)}"
            )
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({"error": f"Invalid face image format: {str(e)}"}), 400
    else:
        # Log the error
        log_entry = AuditLog(
            user_id=user_id, 
            action="Face verification failed: No image provided"
        )
        db.session.add(log_entry)
        db.session.commit()
        return jsonify({"error": "Face image is required"}), 400

    # Find the user by ID
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get client IP for security logging
    client_ip = request.remote_addr
    
    # Verify the face
    verification_result = verify_face(user.face_embedding, captured_image)
    
    if verification_result:
        # Log successful face verification
        log_entry = AuditLog(
            user_id=user_id, 
            action=f"Face verified successfully from IP: {client_ip}"
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({"message": "Face verified successfully"}), 200
    else:
        # Log failed face verification with more details
        log_entry = AuditLog(
            user_id=user_id, 
            action=f"Face verification failed from IP: {client_ip} - Potential unauthorized access attempt"
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({"error": "Face verification failed. Your face doesn't match our records."}), 401

# Generate OTP endpoint
@app.route('/api/generate-otp', methods=['POST'])
def generate_otp_endpoint():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Find the user by ID to get their OTP secret
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate OTP using the user's stored secret key
    otp = generate_otp(user.otp_secret)

    # In a real-world application, you would send this OTP to the user via SMS or email
    # For demo purposes, we're just returning a message
    
    # Log OTP generation
    log_entry = AuditLog(user_id=user_id, action="OTP generated")
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"message": "OTP generated successfully"}), 200

# Verify OTP endpoint
@app.route('/api/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Parse request data
    data = request.json
    otp = data.get('otp')

    if not otp:
        return jsonify({"error": "OTP is required"}), 400

    # Find the user by ID to get their OTP secret
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Verify the OTP using the user's stored secret
    if verify_otp(user.otp_secret, otp):
        # Log successful OTP verification
        log_entry = AuditLog(user_id=user_id, action="OTP verified successfully")
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({"message": "OTP verified successfully"}), 200
    else:
        # Log failed OTP verification
        log_entry = AuditLog(user_id=user_id, action="OTP verification failed")
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({"error": "Invalid OTP"}), 401

# Get passwords endpoint
@app.route('/api/get-passwords', methods=['GET'])
def get_passwords():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Retrieve all password entries for the user
    password_entries = PasswordEntry.query.filter_by(user_id=user_id).all()
    if not password_entries:
        return jsonify({"message": "No passwords found", "passwords": []}), 200

    # Decrypt passwords
    decrypted_passwords = []
    for entry in password_entries:
        decrypted_password = decrypt_data(entry.encrypted_password)
        decrypted_passwords.append({
            "id": entry.id,
            "website_name": entry.website_name,
            "website_url": entry.website_url,
            "password": decrypted_password
        })

    # Log password access
    log_entry = AuditLog(user_id=user_id, action="Retrieved stored passwords")
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"passwords": decrypted_passwords}), 200

# Secure Show Passwords endpoint (requires both face and OTP verification)
@app.route('/api/secure-get-passwords', methods=['POST'])
def secure_get_passwords():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    # Get the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Parse request data
    data = request.json
    face_image_base64 = data.get('face_image')
    otp = data.get('otp')
    
    # Validate input
    if not face_image_base64:
        return jsonify({"error": "Face image is required"}), 400
    if not otp:
        return jsonify({"error": "OTP is required"}), 400
    
    # Verify face
    try:
        captured_image = base64.b64decode(face_image_base64)
        verification_result = verify_face(user.face_embedding, captured_image)
        
        if not verification_result:
            # Log failed face verification
            log_entry = AuditLog(
                user_id=user_id, 
                action=f"Secure password access: Face verification failed from IP: {request.remote_addr}"
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return jsonify({"error": "Face verification failed. Your face doesn't match our records."}), 401
    except Exception as e:
        # Log the error
        log_entry = AuditLog(
            user_id=user_id, 
            action=f"Secure password access: Face verification error - {str(e)}"
        )
        db.session.add(log_entry)
        db.session.commit()
        return jsonify({"error": f"Error processing face image: {str(e)}"}), 400
    
    # Verify OTP
    if not verify_otp(user.otp_secret, otp):
        # Log failed OTP verification
        log_entry = AuditLog(
            user_id=user_id, 
            action=f"Secure password access: OTP verification failed from IP: {request.remote_addr}"
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return jsonify({"error": "Invalid OTP. Please try again."}), 401
    
    # If both face and OTP verification passed, retrieve passwords
    password_entries = PasswordEntry.query.filter_by(user_id=user_id).all()
    if not password_entries:
        return jsonify({"message": "No passwords found", "passwords": []}), 200
    
    # Decrypt passwords
    decrypted_passwords = []
    for entry in password_entries:
        decrypted_password = decrypt_data(entry.encrypted_password)
        decrypted_passwords.append({
            "id": entry.id,
            "website_name": entry.website_name,
            "website_url": entry.website_url,
            "password": decrypted_password
        })
    
    # Log successful password access with enhanced security
    log_entry = AuditLog(
        user_id=user_id, 
        action=f"Retrieved stored passwords with multi-factor authentication from IP: {request.remote_addr}"
    )
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"passwords": decrypted_passwords}), 200

# Delete password endpoint
@app.route('/api/delete-password/<int:password_id>', methods=['DELETE'])
def delete_password(password_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Find the password entry
    password_entry = PasswordEntry.query.filter_by(id=password_id, user_id=user_id).first()
    if not password_entry:
        return jsonify({"error": "Password not found or you don't have permission to delete it"}), 404

    # Delete the password entry
    try:
        website_name = password_entry.website_name  # Store for logging
        db.session.delete(password_entry)
        
        # Log the deletion
        log_entry = AuditLog(user_id=user_id, action=f"Deleted password for {website_name}")
        db.session.add(log_entry)
        
        db.session.commit()
        return jsonify({"message": "Password deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting password: {str(e)}")
        return jsonify({"error": f"Failed to delete password: {str(e)}"}), 500

# Update password endpoint
@app.route('/api/update-password/<int:password_id>', methods=['PUT'])
def update_password(password_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    # Parse request data
    data = request.json
    website_name = data.get('website_name')
    website_url = data.get('website_url')
    password = data.get('password')

    # Validate input
    if not all([website_name, website_url, password]):
        return jsonify({"error": "All fields are required"}), 400

    # Find the password entry
    password_entry = PasswordEntry.query.filter_by(id=password_id, user_id=user_id).first()
    if not password_entry:
        return jsonify({"error": "Password not found or you don't have permission to update it"}), 404

    try:
        # Encrypt the new password
        encrypted_password = encrypt_data(password)
        
        # Store the original website name for logging if it changes
        original_website_name = password_entry.website_name
        
        # Update the password entry
        password_entry.website_name = website_name
        password_entry.website_url = website_url
        password_entry.encrypted_password = encrypted_password
        
        # Log the update
        if original_website_name != website_name:
            log_message = f"Updated password for {original_website_name} (renamed to {website_name})"
        else:
            log_message = f"Updated password for {website_name}"
            
        log_entry = AuditLog(user_id=user_id, action=log_message)
        db.session.add(log_entry)
        
        db.session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating password: {str(e)}")
        return jsonify({"error": f"Failed to update password: {str(e)}"}), 500

# Generate password endpoint
@app.route('/api/generate-password', methods=['GET'])
def generate_password_endpoint():
    length = request.args.get('length', default=12, type=int)
    if length < 8:
        return jsonify({"error": "Password length must be at least 8 characters"}), 400

    # Generate a strong random password
    password = generate_password(length)
    return jsonify({"password": password}), 200

# Default login endpoint for development
@app.route('/api/dev-login', methods=['GET'])
def dev_login():
    # Create or get default user
    default_user = User.query.filter_by(email="default@test.com").first()
    
    if not default_user:
        # Create a default user if it doesn't exist
        hashed_password = bcrypt.hashpw("defaultpass123".encode('utf-8'), bcrypt.gensalt())
        default_user = User(
            name="Default User",
            email="default@test.com",
            password_hash=hashed_password.decode('utf-8'),
            phone_number="1234567890",
            face_embedding=b"default_embedding",
            otp_secret="DEFAULTSECRET123"
        )
        db.session.add(default_user)
        db.session.commit()
    
    # Generate token
    token = jwt.encode(
        {'user_id': default_user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},
        app.config['SECRET_KEY'], algorithm='HS256'
    )
    
    return jsonify({
        "message": "Development login successful",
        "token": token,
        "user_id": default_user.id
    }), 200

# Security logging endpoint
@app.route('/api/security/log', methods=['POST'])
def security_log_endpoint():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
        
    data = request.json
    event_type = data.get('event_type')
    details = data.get('details', '')
    
    if not event_type:
        return jsonify({"error": "Event type is required"}), 400
        
    # Create security log entry
    log_entry = AuditLog(
        user_id=user_id,
        action=f"SECURITY: {event_type} - {details} from IP: {request.remote_addr}"
    )
    db.session.add(log_entry)
    db.session.commit()
    
    return jsonify({"message": "Security event logged successfully"}), 200

# Authentication status endpoint
@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401
    
    # Get the user
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Return basic user info and security status
    return jsonify({
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "face_registered": user.face_embedding is not None,
        "otp_setup_complete": user.otp_secret is not None,
        "last_login": get_last_login(user.id)
    }), 200

# Helper function to get last login time
def get_last_login(user_id):
    last_login = AuditLog.query.filter(
        AuditLog.user_id == user_id,
        AuditLog.action.like("User logged in%")
    ).order_by(AuditLog.timestamp.desc()).first()
    
    if last_login:
        return last_login.timestamp.isoformat()
    return None

# Dummy implementations of missing utilities for demonstration purposes
# In a real application, you would implement these properly in separate files

# utils/encryption.py
def encrypt_data(data):
    try:
        from cryptography.fernet import Fernet
        import base64
        import os
        
        # Use SECRET_KEY to derive a suitable encryption key
        key_bytes = app.config['SECRET_KEY'].encode('utf-8')
        # Ensure the key is 32 bytes for Fernet (using SHA-256 hash)
        import hashlib
        key = base64.urlsafe_b64encode(hashlib.sha256(key_bytes).digest())
        
        cipher_suite = Fernet(key)
        encrypted_data = cipher_suite.encrypt(data.encode('utf-8'))
        return encrypted_data.decode('utf-8')  # Convert bytes to string for storage
    except ImportError:
        print("Warning: cryptography module not available. Using insecure encryption.")
        # Fallback to simple obfuscation (NOT secure for production)
        return f"encrypted_{data}"

def decrypt_data(encrypted_data):
    try:
        from cryptography.fernet import Fernet
        import base64
        import hashlib
        
        # Handle legacy unencrypted data
        if encrypted_data.startswith("encrypted_"):
            return encrypted_data[10:]
        
        # Use SECRET_KEY to derive the same encryption key
        key_bytes = app.config['SECRET_KEY'].encode('utf-8')
        # Ensure the key is 32 bytes for Fernet (using SHA-256 hash)
        key = base64.urlsafe_b64encode(hashlib.sha256(key_bytes).digest())
        
        cipher_suite = Fernet(key)
        try:
            decrypted_data = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting data: {str(e)}")
            # If decryption fails, return the encrypted data as-is
            return encrypted_data
    except ImportError:
        print("Warning: cryptography module not available. Using insecure decryption.")
        # Fallback for simple obfuscation
        if encrypted_data.startswith("encrypted_"):
            return encrypted_data[10:]
        return encrypted_data

# utils/biometric.py
def verify_face(stored_embedding, captured_image):
    try:
        import numpy as np
        import cv2
        from io import BytesIO
        from PIL import Image
        import pickle
        
        # Convert stored embedding from bytes to numpy array
        stored_embedding_array = pickle.loads(stored_embedding)
        
        # Process the captured image to get face embedding
        # Convert bytes to image
        img = Image.open(BytesIO(captured_image))
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Load face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Detect faces
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            print("No face detected in the captured image")
            return False
        
        # Get the largest face
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Extract face ROI
        face_roi = img_cv[y:y+h, x:x+w]
        
        # Resize to a standard size
        face_roi = cv2.resize(face_roi, (128, 128))
        
        # Convert to grayscale and flatten for simple comparison
        face_roi_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        captured_embedding = face_roi_gray.flatten().astype(np.float32)
        
        # Normalize embeddings
        stored_norm = np.linalg.norm(stored_embedding_array)
        captured_norm = np.linalg.norm(captured_embedding)
        
        if stored_norm == 0 or captured_norm == 0:
            return False
            
        stored_embedding_normalized = stored_embedding_array / stored_norm
        captured_embedding_normalized = captured_embedding / captured_norm
        
        # Calculate cosine similarity
        similarity = np.dot(stored_embedding_normalized, captured_embedding_normalized)
        
        # Log the similarity score for debugging
        print(f"Face similarity score: {similarity}")
        
        # Threshold for face verification (adjust based on testing)
        threshold = 0.75
        
        return similarity > threshold
        
    except Exception as e:
        print(f"Error in face verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# utils/password_generator.py
def generate_password(length=12):
    import random
    import string
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

# utils/mfa.py
def generate_secret_key():
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + '234567') for _ in range(16))

def generate_otp(secret_key):
    # In a real implementation, this would use TOTP algorithm
    # This is just a placeholder
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

def verify_otp(secret_key, otp):
    # Replace placeholder implementation with proper TOTP verification
    try:
        import pyotp
        totp = pyotp.TOTP(secret_key)
        return totp.verify(otp)
    except ImportError:
        # Fall back to dummy implementation if pyotp is not available
        print("Warning: pyotp module not available. Using insecure OTP verification.")
        return True  # Note: This should be replaced with proper validation in production

def get_qr_code_url(secret_key, email):
    # Generate Google Authenticator compatible QR code URL using proper TOTP format
    try:
        import pyotp
        totp = pyotp.TOTP(secret_key)
        return totp.provisioning_uri(name=email, issuer_name="Password Manager")
    except ImportError:
        # Fallback to placeholder URL if pyotp is not available
        print("Warning: pyotp module not available. Using placeholder QR code URL.")
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=otpauth://totp/PasswordManager:{email}?secret={secret_key}&issuer=PasswordManager"

if __name__ == '__main__':
    import time
    import os.path
    
    # Check for required dependencies
    missing_packages = []
    try:
        import pyotp
    except ImportError:
        missing_packages.append("pyotp")
    
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        missing_packages.append("cryptography")
    
    try:
        import cv2
    except ImportError:
        missing_packages.append("opencv-python")
    
    try:
        import numpy as np
    except ImportError:
        missing_packages.append("numpy")
    
    try:
        from PIL import Image
    except ImportError:
        missing_packages.append("Pillow")
    
    if missing_packages:
        print("WARNING: The following required packages are missing:")
        for pkg in missing_packages:
            print(f" - {pkg}")
        print("\nTo install these packages, run: pip install " + " ".join(missing_packages))
        print("Or: pip install -r requirements.txt\n")
    
    # Try to initialize the database with retries
    max_retries = 5
    retry_count = 0
    db_initialized = False
    
    while retry_count < max_retries and not db_initialized:
        try:
            with app.app_context():
                # Configure SQLite to handle concurrent access better
                with db.engine.connect() as conn:
                    conn.execute(text("PRAGMA journal_mode=WAL;"))
                    conn.execute(text("PRAGMA busy_timeout=5000;"))
                db.create_all()  # Create database tables
                db_initialized = True
                print("Database initialized successfully")
        except Exception as e:
            retry_count += 1
            print(f"Error initializing database (attempt {retry_count}/{max_retries}): {str(e)}")
            
            # If database is locked and this is not the last retry
            if "database is locked" in str(e).lower() and retry_count < max_retries:
                print("Database is locked. Waiting before retry...")
                time.sleep(2)  # Wait before retrying
            elif retry_count == max_retries:
                # Last resort: try to remove the database file and recreate it
                db_path = os.path.join(os.path.dirname(__file__), 'password_manager.db')
                if os.path.exists(db_path):
                    try:
                        print(f"Attempting to remove locked database file: {db_path}")
                        os.remove(db_path)
                        print("Database file removed. Will recreate on next attempt.")
                        retry_count -= 1  # Give one more chance after removing the file
                    except Exception as remove_err:
                        print(f"Failed to remove database file: {str(remove_err)}")
    
    if not db_initialized:
        print("Failed to initialize database after multiple attempts. Exiting.")
        exit(1)
    
    print("\n-------------------------------------------")
    print("Password Manager Backend with Biometric Authentication")
    print("-------------------------------------------")
    print("Server is running at: http://0.0.0.0:5000")
    print("API Documentation:")
    print(" - POST /api/signup: Register a new user")
    print(" - POST /api/login: Authenticate user and get token")
    print(" - POST /api/add-password: Add a new password entry")
    print(" - GET  /api/get-passwords: Get all passwords (basic authentication)")
    print(" - POST /api/secure-get-passwords: Get passwords with biometric+OTP verification")
    print(" - PUT  /api/update-password/<id>: Update a password entry")
    print(" - DEL  /api/delete-password/<id>: Delete a password entry")
    print(" - GET  /api/generate-password: Generate a strong password")
    print(" - POST /api/verify-face: Verify face authentication")
    print(" - POST /api/generate-otp: Generate an OTP")
    print(" - POST /api/verify-otp: Verify an OTP")
    print(" - GET  /api/auth/status: Get user authentication status")
    print(" - POST /api/security/log: Log security events")
    print("-------------------------------------------")
        
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)