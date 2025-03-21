import pyotp
import base64

# Generate a secret key for each user (in production, store this securely in the database)
def generate_secret_key():
    return pyotp.random_base32()

# Generate an OTP based on the secret key
def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

# Verify the OTP entered by the user
def verify_otp(secret_key, otp):
    totp = pyotp.TOTP(secret_key)
    return totp.verify(otp)

def get_qr_code_url(secret_key, email):
    # Generate a URL for the QR code
    return f"otpauth://totp/PasswordManager:{email}?secret={secret_key}&issuer=PasswordManager"