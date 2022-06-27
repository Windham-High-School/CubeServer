"""Generates a SECRET_KEY so the same one isn't published on GitHub for all to see :)

Command-line flags:
-h/--help   Shows this help message
-f/--force  Forces the replacement of the key
"""

from secrets import token_hex
from os.path import exists
from sys import argv

from app.config import SECRET_KEY_FILE, SECRET_KEY_FILE_ENCODING

def write_new_key():
    """Writes a new key to the key file"""
    with open(SECRET_KEY_FILE, "w", encoding=SECRET_KEY_FILE_ENCODING) as file:
        file.write(token_hex(128))

def check_secrets():
    """Writes a new key only if one does not already exist"""
    if not exists(SECRET_KEY_FILE):
        print("Generating secret file.")
        write_new_key()
    else:
        print("Leaving existing secret file.")

if __name__ == "__main__":
    if "-h" in argv or "--help" in argv:
        print(__doc__)
    elif "-f" in argv or "--force" in argv:
        print("Generating secret file regardless of prior existence.")
        write_new_key()
    else:
        check_secrets()
