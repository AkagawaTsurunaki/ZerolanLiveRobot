import base64
import hashlib
import secrets


def generate_base64_secret(data: str) -> str:
    """
    Generate SHA256 hash and encode it as Base64 string
    :param data: Original string
    :return: Base64-encoded string
    """
    sha256_hash = hashlib.sha256(data.encode('utf-8')).digest()
    base64_encoded_hash = base64.b64encode(sha256_hash).decode('utf-8')
    return base64_encoded_hash


def do_challenge(password: str, salt: str, challenge: str) -> str:
    base64_secret = generate_base64_secret(password + salt)
    my_auth = generate_base64_secret(base64_secret + challenge)
    return my_auth


def generate_salt(length=16):
    salt = secrets.token_bytes(length)
    return base64.b64encode(salt).decode('utf-8')


def generate_challenge(length=32):
    challenge = secrets.token_bytes(length)
    return base64.b64encode(challenge).decode('utf-8')
