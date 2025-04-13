from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError
import requests, os
from fastapi import Request, HTTPException, status, Depends

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_IDENTIFIER = os.getenv("API_IDENTIFIER")
ALGORITHMS = os.getenv("ALGORITHMS")
API_AUDIENCE=os.getenv("API_IDENTIFIER")


def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    payload = verify_token(token)  # This is your existing verification method
    return payload  # contains sub, email, etc.


from functools import lru_cache

@lru_cache()
def get_jwks():
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    print("📢 Fetching JWKS from:", jwks_url)
    return requests.get(jwks_url).json()

def verify_token(token: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
        print("🔍 Unverified Header:", unverified_header)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token header.")

    rsa_key = {}
    for key in get_jwks()["keys"]:
        print("🧩 Checking JWKS key:", key["kid"])
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except JWTError as e:
            raise HTTPException(status_code=401, detail="Token verification failed.")
    else:
        print("❌ No matching key found for kid:", unverified_header["kid"])
        raise HTTPException(status_code=401, detail="No appropriate key found.")

# http_bearer = HTTPBearer()

# def get_jwk():
#     res = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
#     return res.json()["keys"]

# def verify_jwt(token: str):
#     jwks = get_jwk()
#     unverified_header = jwt.get_unverified_header(token)

#     rsa_key = {}
#     for key in jwks:
#         if key["kid"] == unverified_header["kid"]:
#             rsa_key = {
#                 "kty": key["kty"],
#                 "kid": key["kid"],
#                 "use": key["use"],
#                 "n": key["n"],
#                 "e": key["e"]
#             }
#             break

#     if not rsa_key:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     try:
#         payload = jwt.decode(
#             token,
#             rsa_key,
#             algorithms=[ALGORITHMS],
#             audience=API_IDENTIFIER,
#             issuer=f"https://{AUTH0_DOMAIN}/"
#         )
#         return payload
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=f"Token decode error: {str(e)}")

# def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):
#     token = credentials.credentials
#     return verify_jwt(token)