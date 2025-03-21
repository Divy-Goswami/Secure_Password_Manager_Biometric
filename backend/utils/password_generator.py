import random
import string

def generate_password(length=12):
    """
    Generate a strong random password.
    :param length: Length of the password (default is 12 characters).
    :return: A randomly generated password.
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?/~"

    # Ensure the password contains at least one character from each set
    password = [
        random.choice(lowercase),
        random.choice(uppercase),
        random.choice(digits),
        random.choice(symbols)
    ]

    # Fill the rest of the password with random characters
    for _ in range(length - 4):
        password.append(random.choice(lowercase + uppercase + digits + symbols))

    # Shuffle the password to ensure randomness
    random.shuffle(password)

    return ''.join(password)