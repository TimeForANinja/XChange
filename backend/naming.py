import random
import base64
import uuid
import os

def load_words():
    # List provided by https://github.com/first20hours/google-10000-english
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, 'google-10000-english-usa-no-swears-medium.txt')
    try:
        with open(file_path) as word_file:
            return word_file.read().split()
    except FileNotFoundError:
        # Return none and fall back to base64 in generate_human_id if file not found
        return None

WORDS = load_words()

def generate_base64_id(length: int = 10) -> str:
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:length]

def generate_human_id() -> str:
    if not WORDS:
        return generate_base64_id()
    return "-".join(random.sample(WORDS, 3))
