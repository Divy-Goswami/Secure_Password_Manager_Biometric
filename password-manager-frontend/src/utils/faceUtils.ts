import * as faceapi from 'face-api.js';

// Keep track of loading state to avoid loading models multiple times
let modelsLoaded = false;
let loadingPromise: Promise<void> | null = null;

/**
 * Loads face-api.js models from the specified path.
 * Uses a singleton pattern to ensure models are only loaded once.
 */
export const loadFaceDetectionModels = async (): Promise<void> => {
  // If models are already loaded, return immediately
  if (modelsLoaded) {
    return Promise.resolve();
  }

  // If models are already loading, return the existing promise
  if (loadingPromise) {
    return loadingPromise;
  }

  // Start loading models and save the promise
  loadingPromise = (async () => {
    try {
      console.log("⏳ Loading face detection models...");
      
      // Load only the necessary models
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri("/models"),
        faceapi.nets.faceLandmark68Net.loadFromUri("/models")
      ]);
      
      modelsLoaded = true;
      console.log("✅ Face detection models loaded!");
    } catch (error) {
      console.error("⚠️ Error loading face detection models:", error);
      throw error;
    }
  })();

  return loadingPromise;
};

/**
 * Detects a face in the given HTML video element.
 * @param videoElement The HTML video element to detect a face in
 * @returns Face detection result or null if no face is detected
 */
export const detectFace = async (videoElement: HTMLVideoElement): Promise<faceapi.FaceDetection | null> => {
  if (!modelsLoaded) {
    await loadFaceDetectionModels();
  }

  try {
    // Use lower confidence threshold for more reliable detection
    const options = new faceapi.TinyFaceDetectorOptions({ scoreThreshold: 0.5 });
    const result = await faceapi.detectSingleFace(videoElement, options);
    return result || null;
  } catch (error) {
    console.error("Error during face detection:", error);
    return null;
  }
};

/**
 * Checks if the stored face verification is still valid.
 * @returns True if face verification is valid, false otherwise
 */
export const isFaceVerificationValid = (): boolean => {
  try {
    const storedVerification = localStorage.getItem('faceVerification');
    if (!storedVerification) return false;
    
    const { verified, timestamp } = JSON.parse(storedVerification);
    if (!verified || !timestamp) return false;
    
    // Check if verification is less than 5 minutes old
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
    return now - timestamp < fiveMinutes;
  } catch (error) {
    console.error("Error checking face verification validity:", error);
    return false;
  }
};

/**
 * Stores face verification status in localStorage with a timestamp.
 * @param verified Whether face verification was successful
 */
export const storeFaceVerification = (verified: boolean): void => {
  try {
    if (verified) {
      localStorage.setItem('faceVerification', JSON.stringify({
        verified: true,
        timestamp: Date.now()
      }));
    } else {
      localStorage.removeItem('faceVerification');
    }
  } catch (error) {
    console.error("Error storing face verification:", error);
  }
}; 