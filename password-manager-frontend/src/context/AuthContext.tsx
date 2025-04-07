"use client";

import { createContext, useContext, useState, ReactNode, useEffect } from "react";

interface AuthContextType {
  isFaceVerified: boolean;
  setIsFaceVerified: (verified: boolean) => void;
  faceVerificationTimestamp: number | null;
  setFaceVerificationTimestamp: (timestamp: number | null) => void;
  isOTPVerified: boolean;
  setIsOTPVerified: (verified: boolean) => void;
  isAuthenticated: boolean;
  setIsAuthenticated: (authenticated: boolean) => void;
  checkFaceVerificationValid: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isFaceVerified, setIsFaceVerified] = useState(false);
  const [faceVerificationTimestamp, setFaceVerificationTimestamp] = useState<number | null>(null);
  const [isOTPVerified, setIsOTPVerified] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if the stored face verification in localStorage is still valid
  useEffect(() => {
    const storedVerification = localStorage.getItem('faceVerification');
    if (storedVerification) {
      try {
        const { verified, timestamp } = JSON.parse(storedVerification);
        if (verified && timestamp) {
          // Check if verification is less than 5 minutes old
          const now = Date.now();
          const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
          if (now - timestamp < fiveMinutes) {
            setIsFaceVerified(true);
            setFaceVerificationTimestamp(timestamp);
          } else {
            // Clear expired verification
            localStorage.removeItem('faceVerification');
          }
        }
      } catch (error) {
        console.error("Error parsing stored face verification:", error);
        localStorage.removeItem('faceVerification');
      }
    }
  }, []);

  // Effect to update localStorage when face verification changes
  useEffect(() => {
    if (isFaceVerified) {
      const timestamp = Date.now();
      setFaceVerificationTimestamp(timestamp);
      localStorage.setItem('faceVerification', JSON.stringify({
        verified: true,
        timestamp
      }));
    } else if (!isFaceVerified && faceVerificationTimestamp !== null) {
      setFaceVerificationTimestamp(null);
      localStorage.removeItem('faceVerification');
    }
  }, [isFaceVerified]);

  // Function to check if face verification is still valid
  const checkFaceVerificationValid = (): boolean => {
    if (!isFaceVerified || !faceVerificationTimestamp) return false;
    
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
    return now - faceVerificationTimestamp < fiveMinutes;
  };

  return (
    <AuthContext.Provider
      value={{
        isFaceVerified,
        setIsFaceVerified,
        faceVerificationTimestamp,
        setFaceVerificationTimestamp,
        isOTPVerified,
        setIsOTPVerified,
        isAuthenticated,
        setIsAuthenticated,
        checkFaceVerificationValid
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
