import base64
import hashlib
import os
import requests
import jwt  # PyJWT library to decode and verify JWT tokens
from urllib.parse import urlencode


# Step 1: Generate PKCE Code Verifier and Code Challenge
def generate_code_verifier():
    # Generate a random 43 to 128 characters code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).decode("utf-8").rstrip("=")
    return code_verifier


def generate_code_challenge(code_verifier):
    # Generate SHA256 hash of the code verifier and base64 URL encode it
    sha256 = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(sha256).decode("utf-8").rstrip("=")
    return code_challenge


# Step 2: Request Authorization Code from Keycloak
def get_authorization_code(client_id, redirect_uri, code_challenge):
    authorization_url = (
        "http://localhost:8080/realms/example-realm/protocol/openid-connect/auth"
    )

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid",
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    }

    # Construct the full authorization URL
    auth_url = f"{authorization_url}?{urlencode(params)}"
    print(f"Go to this URL to authorize:\n{auth_url}")
    return auth_url


# Step 3: Exchange Authorization Code for Access Token
def get_access_token(auth_code, client_id, redirect_uri, code_verifier):
    token_url = (
        "http://localhost:8080/realms/example-realm/protocol/openid-connect/token"
    )

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }

    # Send a POST request to exchange the authorization code for an access token
    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        return response.json()  # Return JSON containing tokens
    else:
        print("Error obtaining access token:", response.text)
        return None


# Step 4: Fetch JWKS from Keycloak
def get_jwks(jwks_url):
    try:
        response = requests.get(jwks_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching JWKS: {e}")
        return None


# Step 5: Verify JWT Signature Using the Public Key
def verify_jwt(jwt_token, jwks_url):
    try:
        # Fetch JWKS
        jwks = get_jwks(jwks_url)
        if not jwks:
            return None

        # Extract the header from the JWT
        unverified_header = jwt.get_unverified_header(jwt_token)
        if not unverified_header or "kid" not in unverified_header:
            print("Invalid JWT header: missing 'kid'")
            return None

        # Find the matching key in the JWKS
        kid = unverified_header["kid"]
        public_key = None
        for key in jwks["keys"]:
            if key["kid"] == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not public_key:
            print("Public key not found in JWKS")
            return None

        # Decode and verify the JWT in one step
        decoded_token = jwt.decode(
            jwt_token,
            public_key,
            algorithms=["RS256"],
            options={"verify_exp": True},  # Ensures token expiration is checked
        )
        print("JWT verified successfully!")
        return decoded_token

    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None


# Step 6: Refresh Access Token Using Refresh Token
def refresh_access_token(refresh_token, client_id, token_url):
    try:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        }
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        print("Access token refreshed successfully!")
        return tokens
    except requests.RequestException as e:
        print(f"Error refreshing token: {e}")
        return None


# Main function for the full flow
def main():
    # Configuration (replace with your actual Keycloak details)
    client_id = "myclient"
    redirect_uri = "http://localhost:8080/callback"  # Replace with your redirect URI
    jwks_url = (
        "http://localhost:8080/realms/example-realm/protocol/openid-connect/certs"
    )
    token_url = (
        "http://localhost:8080/realms/example-realm/protocol/openid-connect/token"
    )

    # Step 1: Generate PKCE Code Verifier and Challenge
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    print("Code Verifier:", code_verifier)
    print("Code Challenge:", code_challenge)

    # Step 2: Get Authorization Code
    auth_url = get_authorization_code(client_id, redirect_uri, code_challenge)
    print(
        "\nAfter logging in, you'll be redirected. Copy the authorization code from the URL and paste it here."
    )
    auth_code = input("Enter the authorization code: ")

    # Step 3: Exchange Authorization Code for Access Token
    token_response = get_access_token(auth_code, client_id, redirect_uri, code_verifier)
    if token_response:
        print("\nAccess Token Response:", token_response)

        # Step 4: Verify the JWT Access Token
        access_token = token_response.get("access_token")
        if access_token:
            verified_claims = verify_jwt(access_token, jwks_url)
            if verified_claims:
                print("\nVerified JWT Claims:")
                print(verified_claims)

        # Step 5: Refresh Access Token (Optional)
        refresh_token = token_response.get("refresh_token")
        if refresh_token:
            print("\nAttempting to refresh the access token...")
            new_tokens = refresh_access_token(refresh_token, client_id, token_url)
            if new_tokens:
                print("New Tokens:")
                print(new_tokens)
    else:
        print("Failed to obtain access token.")


if __name__ == "__main__":
    main()
