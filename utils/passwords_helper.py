from passlib.context import CryptContext
import random
import string
import secrets
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password:str) -> str:
    return pwd_context.hash(password)


def verify(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password,hashed_password)



def generate_password(length: int =16):
    # Define the character sets
    letters = string.ascii_letters  # a-z, A-Z
    digits = string.digits  # 0-9

    # Ensure the password contains at least one letter, digit, and special character
    password_chars = [
        random.choice(letters),
        random.choice(digits),
    ]

    # Fill the rest of the password length with a random combination of characters
    password_chars += random.choices(letters + digits , k=length - 2)

    # Shuffle the password to ensure randomness and convert to a string
    random.shuffle(password_chars)
    return ''.join(password_chars)
