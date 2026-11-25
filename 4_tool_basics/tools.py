from datetime import datetime

def get_current_time():
    """Returns the current time as a formatted string."""
    return datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")

import random
def roll_dice(sides=6):
    """Simulates rolling a dice with the given number of sides."""
    return random.randint(1, sides)

import secrets
import string

def generate_password(length=12):

    charecters = (string.ascii_letters + string.digits + string.punctuation)

    password=""

    for _ in range(length):
        password += secrets.choice(charecters)
    return password