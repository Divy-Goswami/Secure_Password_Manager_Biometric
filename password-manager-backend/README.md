# Password Manager Backend

This is the backend server for the Password Manager application, providing secure API endpoints for user authentication, password management, biometric verification, and OTP validation.

## Features

- **User Authentication**: Registration, login, and token-based authentication
- **Password Management**: CRUD operations for storing and retrieving encrypted passwords
- **Biometric Authentication**: Support for face recognition and fingerprint verification
- **OTP Verification**: Implements One-Time Password validation for multi-factor authentication
- **Secure Storage**: Passwords stored with encryption
- **RESTful API**: Well-documented endpoints following REST principles

## Technology Stack

- **Python**: Core programming language
- **Django**: Web framework
- **Django REST Framework**: For building the RESTful API
- **SQLite**: Database (development)
- **JWT Authentication**: For secure token-based authentication

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd password-manager-backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   cd password_manager
   python manage.py migrate
   ```

5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`.

## API Endpoints

- **Authentication**:
  - `POST /api/users/register/`: Register a new user
  - `POST /api/users/login/`: Login and receive a token
  - `POST /api/users/verify-face/`: Verify face biometrics
  - `POST /api/users/verify-otp/`: Verify OTP

- **Password Management**:
  - `GET /api/users/passwords/`: Retrieve all passwords for a user
  - `POST /api/users/passwords/`: Create a new password entry
  - `PUT /api/users/passwords/{id}/`: Update a password entry
  - `DELETE /api/users/passwords/{id}/`: Delete a password entry

## Security Features

- Password hashing using Django's security functions
- JWT token-based authentication
- Encrypted storage of sensitive information
- Biometric verification for enhanced security
- OTP validation for two-factor authentication

## Development Guidelines

- Follow PEP 8 style guide for Python code
- Write tests for new features
- Document all API endpoints

## License

This project is licensed under the MIT License.
