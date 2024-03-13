import requests
import jwt
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


def base64url_decode(input):
    # Adds padding to the input before decoding
    rem = len(input) % 4
    if rem > 0:
        input += '=' * (4 - rem)
    return base64.urlsafe_b64decode(input)


def construct_rsa_public_key(n, e):
    # Decode the base64url encoded values
    decoded_n = base64url_decode(n)
    decoded_e = base64url_decode(e)

    # Convert to integers
    int_n = int.from_bytes(decoded_n, byteorder='big')
    int_e = int.from_bytes(decoded_e, byteorder='big')

    # Construct RSA Public Key
    return rsa.RSAPublicNumbers(e=int_e, n=int_n).public_key(default_backend())


def get_rsa_public_key(jwks, kid):
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return construct_rsa_public_key(key['n'], key['e'])
    raise Exception("Public key not found in JWKS")


def get_public_key(jwks_uri, kid):
    jwks_response = requests.get(jwks_uri)
    jwks = jwks_response.json()
    key = next((key for key in jwks['keys'] if key['kid'] == kid), None)
    if not key:
        raise Exception("Public key not found in JWKS")
    return get_rsa_public_key(jwks, kid)


def validate_jwt(token, jwks_uri):
    unverified_header = jwt.get_unverified_header(token)
    public_key = get_public_key(jwks_uri, unverified_header['kid'])
    return public_key


def decode_jwt(token, public_key, audience, issuer):
    try:
        return jwt.decode(token, public_key, algorithms=["RS256"], audience=audience, issuer=issuer)
    except Exception as e:
        print(e)
        return None
