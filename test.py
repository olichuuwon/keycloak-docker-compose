import requests

jwks_url = "http://localhost:8080/realms/example-realm/protocol/openid-connect/certs"
response = requests.get(jwks_url)
print("JWKS Response:", response.json())
