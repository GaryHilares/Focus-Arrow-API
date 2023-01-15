from string import ascii_lowercase, ascii_uppercase, digits
import random

def generate_pin():
    return "".join([random.choice(ascii_lowercase + ascii_uppercase + digits) for _ in range(8)])