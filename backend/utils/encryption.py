from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# AES Encryption Key (should be securely stored in production)
AES_KEY = os.urandom(32)  # 256-bit key
AES_IV = os.urandom(16)   # Initialization vector

def encrypt_data(data):
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CFB(AES_IV), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    return encrypted_data

def decrypt_data(encrypted_data):
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CFB(AES_IV), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
    return decrypted_data.decode('utf-8')