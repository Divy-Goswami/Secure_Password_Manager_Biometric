# Password Manager with Biometric Authentication

A comprehensive password management application with multi-factor authentication, including **biometric verification** (Face ID) and **OTP validation**. This application allows users to securely store, manage, and retrieve passwords for various services.

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
  - Automatic session timeout
  - Secure storage with modern encryption algorithms
- **User-friendly Interface**:
  - Responsive design for mobile and desktop
  - Dark/light mode toggle
  - Password categorization and search functionality

## Technology Stack

- **Next.js**: React framework for server-side rendering
- **TypeScript**: For type-safe code
- **Tailwind CSS**: Utility-first CSS framework
- **JWT**: For secure authentication
- **Face API**: For biometric authentication
- **React Context API**: For state management

## Getting Started

### Prerequisites

Make sure you have the following installed:

- [Node.js](https://nodejs.org/) (v16 or higher)
- [npm](https://www.npmjs.com/) or [Yarn](https://classic.yarnpkg.com/en/docs/install/)

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd password-manager-frontend
   ```

2. **Install dependencies**:

   Using npm:

   ```bash
   npm install
   ```

   Using Yarn:

   ```bash
   yarn install
   ```

3. **Set up environment variables**:

   Create a `.env.local` file in the root directory with the following variables:

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```

4. **Run the development server**:

   Using npm:

   ```bash
   npm run dev
   ```

   Using Yarn:

   ```bash
   yarn dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

## Project Structure

- **`/src/app`**: Next.js pages and routes
- **`/src/components`**: Reusable UI components
- **`/src/context`**: React Context providers for global state
- **`/src/utils`**: Utility functions and helpers
- **`/src/styles`**: Global styles and Tailwind configuration

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

3. **Password Management**:
   - User can add, view, edit, and delete passwords
   - Passwords are encrypted before being sent to the server
   - Master password is used for additional security when viewing sensitive information

## Development Guidelines

- Follow TypeScript best practices
- Write clean, reusable components
- Document code with comments
- Use proper state management patterns
- Write tests for components and utilities

## Integration with Backend

This frontend application communicates with a Django backend API. Make sure to set up and run the backend server before using this application. See the backend repository for setup instructions.

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Create a Pull Request

## License

This project is licensed under the MIT License.

---
