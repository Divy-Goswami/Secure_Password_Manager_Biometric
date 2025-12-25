// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
  // Auth
  TOKEN_REFRESH: `${API_BASE_URL}/api/token/refresh/`,
  
  // User
  USER_ME: `${API_BASE_URL}/api/users/me/`,
  USER_IMAGE: `${API_BASE_URL}/api/users/image/`,
  USER_IMAGE_UPLOAD: `${API_BASE_URL}/api/users/image-upload/`,
  
  // OTP
  SEND_OTP_EMAIL: `${API_BASE_URL}/api/users/send-otp-email/`,
  VERIFY_OTP: (otp: string) => `${API_BASE_URL}/api/users/verify-otp/?otp=${otp}`,
  
  // Face ID
  VERIFY_FACE_ID: `${API_BASE_URL}/api/users/verify-face-id/`,
  
  // Password Management
  ADD_PASSWORD: `${API_BASE_URL}/api/users/add_password/`,
};

export default API_BASE_URL;
