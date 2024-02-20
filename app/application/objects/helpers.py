import random
import string


# https://stackoverflow.com/a/30779367
def generate_list_id() -> str:
    """Generates a uniquely random alphanumeric 8 character string as the list_id"""
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=8))
