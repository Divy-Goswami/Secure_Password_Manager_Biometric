# Secure Password Manager with Biometric Authentication

A secure and comprehensive password management solution with multi-factor authentication, including **biometric verification** (Face ID) and **OTP validation**. This application allows users to securely store, manage, and retrieve passwords for various services.

## Features

- **Multi-factor Authentication**:
  - Biometric verification (Face ID/fingerprint)
  - One-Time Password (OTP) validation
  - Email and password authentication
- **User Authentication**:
  - Secure login with JWT token-based authentication
  - New user registration with email verification
  - Password reset functionality
- **Password Management**:
  - Create, view, edit, and delete password entries
  - Auto-generate secure passwords
  - Copy passwords to clipboard with auto-clear feature
  - Password strength indicator
- **Security**:
  - Client-side encryption of sensitive data
  - Server-side encryption of stored passwords
  - Automatic session timeout
  - Secure storage with modern encryption algorithms
- **User-friendly Interface**:
  - Responsive design for mobile and desktop
  - Dark/light mode toggle
  - Password categorization and search functionality

## Repository Structure

This repository contains both the frontend and backend components:

- **`/password-manager-frontend`**: Next.js application with TypeScript and Tailwind CSS
- **`/password-manager-backend`**: Django REST Framework application with Python

## Technology Stack

### Frontend
- Next.js (React framework for SSR)
- TypeScript
- Tailwind CSS
- Face-api.js (for biometric authentication)
- React Context API (for state management)

### Backend
- Python
- Django
- Django REST Framework
- JWT Authentication
- SQLite (development) / PostgreSQL (production)
- Face recognition libraries

## Getting Started

### Prerequisites

- Node.js v16+ and npm/yarn for the frontend
- Python 3.8+ and pip for the backend

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Divy-Goswami/Secure_Password_Manager_Biometric.git
   cd Secure_Password_Manager_Biometric
   ```

2. **Set up the backend**:
   ```bash
   cd password-manager-backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   
   cd password_manager
   python manage.py migrate
   python manage.py runserver
   ```

3. **Set up the frontend**:
   ```bash
   cd ../password-manager-frontend
   npm install
   # or
   yarn install
   
   # Create .env.local with:
   # NEXT_PUBLIC_API_URL=http://localhost:8000/api
   
   npm run dev
   # or
   yarn dev
   ```

4. Open your browser at [http://localhost:3000](http://localhost:3000)

## Authentication Flow

1. **Registration**:
   - User provides name, email, and password
   - Email verification is sent
   - User uploads their face data for biometric authentication
   - User sets up OTP with Google Authenticator

2. **Login**:
   - User enters email and password
   - Upon successful credential verification, face verification is required
   - After successful biometric verification, OTP verification is required
   - Upon successful OTP verification, user is granted access to the dashboard

## API Endpoints

### Authentication
- `POST /api/users/register/`: Register a new user
- `POST /api/users/login/`: Login and receive a token
- `POST /api/users/verify-face/`: Verify face biometrics
- `POST /api/users/verify-otp/`: Verify OTP

### Password Management
- `GET /api/users/passwords/`: Retrieve all passwords for a user
- `POST /api/users/passwords/`: Create a new password entry
- `PUT /api/users/passwords/{id}/`: Update a password entry
- `DELETE /api/users/passwords/{id}/`: Delete a password entry

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Author

Created by Divy Goswami 