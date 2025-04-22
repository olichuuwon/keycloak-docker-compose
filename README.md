# Keycloak Docker Compose

This guide provides details on running Keycloak with or without PostgreSQL, best practices for configuring realms, roles, groups, and users, and practical examples to simplify development and testing. It also covers how to generate and use JWT tokens for API authentication.

---

## Table of Contents

1. [Day 1: Initial Compose Setup](#day-1-initial-compose-setup)
2. [Day 2: Example API Request](#day-2-example-api-request)
3. [Day 3: Authorization Code Flow with PKCE](#day-3-authorization-code-flow-with-pkce)

---

## Day 1: Initial Compose Setup

### **When You Can Skip PostgreSQL**

You may skip PostgreSQL in the following scenarios:

- **Local Testing or Development**: When testing Keycloak configurations, realms, roles, groups, or authentication flows.
- **Stateless Testing**: If persistence of data between Keycloak restarts is unnecessary.

---

### **Running Keycloak Without PostgreSQL**

Modify your `docker-compose.yml` file to remove PostgreSQL for lightweight testing:

```yaml
version: '3.9'
services:
  keycloak:
    image: quay.io/keycloak/keycloak:22.0
    container_name: keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: admin
    command:
      - start-dev
      - --import-realm
    volumes:
      - ./keycloak-config:/opt/keycloak/data/import
    ports:
      - "8088:8088"
```

In this configuration, Keycloak uses its default **H2 in-memory database**.

#### **Limitations of H2 Database**

- **No Persistence**: Data is lost when the Keycloak container stops.
- **Performance**: Not optimized for concurrent access or large-scale data.
- **Not Production-Ready**: Avoid using H2 in production environments.

---

### **Keycloak Best Practices**

#### **1. Realm Design**

- Use a **single realm** for related applications to simplify management.
- For **multi-tenant systems**, use separate realms per tenant to isolate users and configurations.

#### **2. Roles**

- **Realm Roles**: For permissions that span across all clients in the realm (e.g., `admin`, `user`).
- **Client Roles**: For permissions specific to a client (e.g., `editor` for a specific app).
- Use meaningful, descriptive names (e.g., `reader`, `editor`, `admin`).

#### **3. Groups**

- Define groups for logical or organizational units (e.g., Engineering, HR).
- Use **group attributes** for metadata (e.g., `department`, `region`).
- Assign roles to groups and add users to groups—minimizing direct role assignments to users.

#### **4. User Management**

- Use groups to manage user permissions collectively.
- Avoid assigning roles directly to users unless absolutely necessary.

#### **5. Client Configuration**

- Secure clients with appropriate access types (e.g., **confidential** or **public**).
- Use **client scopes** to manage permissions and claims effectively.

#### **6. Security**

- Enable **TLS** for Keycloak, especially in production.
- Use strong admin credentials and limit access to the admin console.
- Regularly update Keycloak to benefit from security patches.
- Enable **audit logging** to monitor administrative and authentication events.

#### **7. Data Backup and Migration**

- Regularly back up your database (PostgreSQL or H2 for testing).
- Use realm export/import features for managing configurations and migrations.

#### **8. Automation**

- Automate provisioning of users, groups, and roles using Keycloak's Admin REST API.
- Maintain JSON or script-based configurations for reproducibility.

#### **9. Testing Environments**

- Use the embedded H2 database for lightweight testing.
- Match production configurations in staging environments for validation.

#### **10. Monitoring and Scaling**

- Integrate with monitoring tools (e.g., Prometheus, Grafana).
- Plan for scaling by deploying Keycloak in a clustered environment with a load balancer.

---

### **Mannual Role and Group Assignment Example in Keycloak**

#### Create Realm Roles

1. Navigate to **Roles** in the admin console.
2. Add roles `1`, `2`, `3`, `4`, and `5`.

#### Create Groups

1. Navigate to **Groups** in the admin console.
2. Create groups `A`, `B`, and `C`.

#### Assign Roles to Group A

1. Select **Group A** → **Role Mappings**.
2. Assign roles `1` and `5`.

#### Add Users to Groups

1. Navigate to **Users** → Select a user → **Groups** tab.
2. Add the user to groups `A`, `B`, or `C`.

---

### **Multi-Realm JSON Example**

Keycloak allows multiple realms to be defined in a single JSON file for organizational purposes. Below is an example:

```json
[
  {
    "realm": "myrealm",
    "enabled": true,
    "roles": {
      "realm": [
        { "name": "admin" },
        { "name": "user" }
      ]
    },
    "users": [
      {
        "username": "AdminUser",
        "enabled": true,
        "emailVerified": true,
        "credentials": [
          { "type": "password", "value": "admin123" }
        ],
        "realmRoles": ["admin"]
      },
      {
        "username": "NormalUser",
        "enabled": true,
        "emailVerified": true,
        "credentials": [
          { "type": "password", "value": "user123" }
        ],
        "realmRoles": ["user"]
      }
    ],
    "clients": [
      {
        "clientId": "myclient",
        "publicClient": true,
        "redirectUris": ["https://example.com/callback"],
        "directAccessGrantsEnabled": true
      }
    ]
  },
  {
    "realm": "example-realm",
    "enabled": true,
    "roles": {
      "realm": [
        { "name": "1" },
        { "name": "2" },
        { "name": "3" },
        { "name": "4" },
        { "name": "5" }
      ]
    },
    "groups": [
      {
        "name": "A",
        "realmRoles": ["1", "5"],
        "attributes": {
          "team": ["Alpha"]
        }
      },
      {
        "name": "B",
        "attributes": {
          "team": ["Beta"]
        }
      },
      {
        "name": "C",
        "attributes": {
          "team": ["Gamma"]
        }
      }
    ],
    "users": [
      {
        "username": "GroupAUser",
        "enabled": true,
        "emailVerified": true,
        "credentials": [
          { "type": "password", "value": "groupA123" }
        ],
        "groups": ["A"]
      },
      {
        "username": "GroupBUser",
        "enabled": true,
        "emailVerified": true,
        "credentials": [
          { "type": "password", "value": "groupB123" }
        ],
        "groups": ["B"]
      }
    ],
    "clients": [
      {
        "clientId": "myclient",
        "publicClient": false,
        "secret": "mysecret",
        "redirectUris": ["*"],
        "directAccessGrantsEnabled": true
      }
    ]
  }
]

```

---

## Day 2: Example API Request

### 1. Requesting an Access Token

To obtain an access token, use the following `curl` command to send a POST request to the Keycloak server:

```bash
curl -X POST "http://localhost:8088/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoQWcwNFV5VTRtdTFZS2o2Q1pVWWpNUDMxTzV3Z2FYUUtZVVUyT2d2anNF...",
  "expires_in": 300,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiMTBjMmY4MC0wN2RmLTQ4YWEtOTU1Yy1jZTNmYTM1OGMyZTQifQ...",
  "token_type": "Bearer",
  "scope": "profile email"
}
```

### 2. Requesting an Access Token with Client Secret

If your client requires a client secret, add the `client_secret` parameter:

```bash
curl -X POST "http://localhost:8088/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "client_secret=mysecret" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoQWcwNFV5VTRtdTFZS2o2Q1pVWWpNUDMxTzV3Z2FYUUtZVVUyT2d2anNF...",
  "expires_in": 300,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiMTBjMmY4MC0wN2RmLTQ4YWEtOTU1Yy1jZTNmYTM1OGMyZTQifQ...",
  "token_type": "Bearer",
  "scope": "profile email"
}
```

### 3. Fetching Public Keys for Token Verification

To retrieve the public keys used by the Keycloak server for signing tokens, use the following `curl` command:

```bash
curl http://localhost:8088/realms/example-realm/protocol/openid-connect/certs
```

**Response:**

```json
{
  "keys": [
    {
      "kid": "hAg04UyU4mu1YKj6CZUYjMP31O5wgaXQKYUU2OgvjsE",
      "kty": "RSA",
      "alg": "RS256",
      "use": "sig",
      "n": "xpnh36HH2g4D60CazrlXngw60QEe43CqruG6xHC6m7mY9GKXLno6s8pt1FulYv-NNg_GkpECXY5vM8umyJ7mADLev-ujnU3-gC86OHNTAynKIxdxbtOKxS4RYY70MKUkqqrw6CUADJlr3JlPCzD2UD1e2-_QPGmAnanMzdyH-1zWNeWYARq-FXGhhw5629Il_BSi9-tp7Lj9HpUYcbowHEf-B_qPwzP6viORB-dVwi6sOH8F5bfonKj61HyCEjoWU_4Pq-mrbMx31RZ0pQRUkGC-9NC3cSfEv3CFxq-vMAOPGWYigVnNQTRia1ip2PDIH_LD8bOM7jRh6bWb8RAQDw",
      "e": "AQAB",
      "x5c": [
        "MIICqTCCAZECBgGTkCfJijANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDDA1leGFtcGxlLXJlYWxtMB4XDTI0MTIwNDA1MzA0NloXDTM0MTIwNDA1MzIyNlowGDEWMBQGA1UEAwwNZXhhbXBsZS1yZWFsbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMaZ4d+hx9oOA+tAms65V54MOtEBHuNwqq7husRwupu5mPRily56OrPKbdRbpWL/jTYPxpKRAl2ObzPLpsie5gAy3r/ro51N/oAvOjhzUwMpyiMXcW7TisUuEWGO9DClJKqq8OglAAyZa9yZTwsw9lA9Xtvv0DxpgJ2pzM3ch/tc1jXlmAEavhVxoYcOetvSJfwUovfraey4/R6VGHG6MBxH/gf6j8Mz+r4jkQfnVcIurDh/BeW36Jyo+tR8ghI6FlP+D6vpq2zMd9UWdKUEVJBgvvTQt3EnxL9whcavrzADjxlmIoFZzUE0YmtYqdjwyB/yw/GzjO40Yem1m/EQEA8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAlRmlpQu1z8r3FwOn2+qplR7MIU+wZxQZUNF2lm4R7OSldRFtSCyzkJtkE5KcfR/f65bteCq+mYgfi+KcSyaT+acaDAcgJA5ML3+VWhzV4lj4U3FsMeSnk88N4ez+SEuKw5INZ+ZnJVxQ8ih2PnMhPh3oGLhlSYgwbqmEE7AhOeKRjbXqb6zGyamIwjanWRC0qHfpH3J8N7BWUYURSkukhTwvmULM6h1pxcThWPAhYRBMC1Wp92Y4vyR9BMKxxD+1INefUj44vatEblX0GiNjaNS3Mq2NGnM96I4xblOXguRdfKuJ/GRmDE9n3uiz1VuLJ32XX05NCVhtcdholb6N0w=="
      ],
      "x5t": "IRF70_5_8gxoJix40wOc1rNQq3w",
      "x5t#S256": "atlcCri24QZyYH_fww12sE5srd7r-s4Y8IqVGqtQHoE"
    }
  ]
}
```

---

### Notes

- Replace the `client_id`, `client_secret`, `username`, and `password` values with the actual ones from your Keycloak setup.
- Use the tokens (`access_token` and `refresh_token`) in subsequent API calls as needed.
- Public keys retrieved from the `/certs` endpoint can be used to verify JWT signatures for security purposes.

```bash
curl -X POST "http://localhost:8088/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"
```

```bash
curl -X POST "http://localhost:8088/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "client_secret=mysecret" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"

```

```bash
curl http://localhost:8088/realms/example-realm/protocol/openid-connect/certs
```

### Why `client_secret` is needed here

- The `client_secret` is used by Keycloak to authenticate the **client application** (e.g., `myclient`) to ensure that the request is coming from a legitimate client. This is part of **client authentication** and is necessary even though the request also involves user credentials (username and password).
- The `client_id` and `client_secret` authenticate the client to the authorization server, while the username and password are used to authenticate the **user**.
- Keycloak will issue an access token after successfully verifying the **client credentials** and **user credentials**.

However, keep in mind that using the **Password Grant Flow** is not recommended for **public clients** (e.g., mobile apps, client-side JavaScript) because it exposes the `client_secret` in the request. This flow is typically used for **confidential clients**, such as server-side applications that can securely store the `client_secret`.

### **Summary of Key Concepts**

- **JWT (JSON Web Token)**: Used for securely transmitting user or client authentication data.
- **JWKS (JSON Web Key Set)**: A set of public keys used for verifying the JWT's signature.
- **Authorization Code Flow**: Used for user authentication and authorization, where the client receives a JWT after the user logs in.
- **Client Credentials Flow**: Used for client authentication without user involvement, where the client receives a JWT for accessing protected resources.

In both flows, the JWT is the primary method for authenticating API requests, and the JWKS is used to validate the JWT's signature.

When using the **Password Grant Flow** (also known as the **Resource Owner Password Credentials Grant Flow**) with Keycloak or any OAuth2 provider, the client sends the **username** and **password** of the user along with the `client_id` and `client_secret` in exchange for an access token (usually a JWT).

However, this flow has significant security implications for **public clients** (e.g., mobile apps, single-page apps (SPA), or client-side JavaScript). Here's why this approach is not recommended for those types of clients:

### **Risks of Using Password Grant Flow for Public Clients**

1. **Exposing the Client Secret**:
   - In the Password Grant Flow, the client sends the `client_id` and `client_secret` to authenticate itself to the authorization server (Keycloak). 
   - For **confidential clients** (like server-side applications), this is acceptable because the `client_secret` can be securely stored on the server.
   - However, for **public clients**, such as mobile apps or SPAs, the `client_secret` is inherently exposed. In these environments, it's almost impossible to securely store the `client_secret` because it would be included in the client-side code, making it vulnerable to exposure by reverse engineering or network inspection.

2. **Security Vulnerability**:
   - If the client_secret is exposed, it can be exploited by attackers. For example, they could use the exposed `client_secret` to impersonate the client and gain unauthorized access to resources or obtain JWT tokens.
   - This defeats the security purpose of having a secret to authenticate the client.

### Recommended for Other OAuth2 Flows for Public Clients**

1. **Authorization Code Flow (with PKCE)**:
   - The **Authorization Code Flow** is the recommended flow for public clients, especially mobile apps and SPAs.
   - Instead of using the `client_secret`, it relies on the **Proof Key for Code Exchange (PKCE)** to securely exchange an authorization code for an access token.
   - The PKCE mechanism adds an additional layer of security by using a dynamically generated code challenge and code verifier, which mitigates the risk of interception during the authorization process.

   **Why this is safer**
   - The `client_secret` is not used, so there is no sensitive secret to expose.
   - The `code_verifier` is only known by the client and is exchanged for an authorization token after the authorization code is received, preventing attackers from hijacking the authorization process.

   **Example Flow**:
   - The client initiates the flow by sending an authorization request to Keycloak with the `code_challenge` (generated using a cryptographic method).
   - After the user logs in, the client receives an authorization code.
   - The client then sends the authorization code and the `code_verifier` to Keycloak to exchange the code for an access token.

   **Keycloak Example URL**

   ```plaintext
   https://localhost:8088/realms/example-realm/protocol/openid-connect/auth?response_type=code&client_id=myclient&redirect_uri=http://localhost:3000/callback&code_challenge=<code_challenge>&code_challenge_method=S256
   ```

2. **Implicit Flow** (Deprecated but still used in some scenarios):
   - The **Implicit Flow** directly issues an access token (JWT) after successful user authentication without requiring an authorization code exchange.
   - This flow is faster but less secure than the Authorization Code Flow with PKCE because the token is returned directly in the URL fragment.
   - This flow is often deprecated in favor of the more secure **Authorization Code Flow with PKCE**, but it's still used in some applications, especially single-page applications (SPAs).

3. **Client Credentials Flow (for Machine-to-Machine)**:
   - The **Client Credentials Flow** is used for server-to-server authentication, where both the client and the authorization server authenticate each other using the `client_id` and `client_secret`.
   - This is appropriate for **confidential clients**, such as backend services or daemons, but not for public clients like mobile apps.

### **Summary: Why You Should Avoid Password Grant Flow for Public Clients**

- The **Password Grant Flow** requires sending a `client_secret` in the request, which is risky because public clients can't securely store the secret.
- Using this flow exposes the `client_secret`, which could be intercepted or reverse-engineered.
- The recommended flows for **public clients** are the **Authorization Code Flow with PKCE** (for mobile apps, SPAs) and the **Implicit Flow** (though this is less secure and deprecated in favor of Authorization Code Flow with PKCE).

## Day 3: Authorization Code Flow with PKCE

### **Best Practice for Public Clients: Authorization Code Flow with PKCE**

PKCE, pronounced "pixy," is an extension to the OAuth 2.0 Authorization Code Flow designed to prevent authorization code interception attacks. It's particularly useful in mobile and public clients (e.g., single-page applications or native mobile apps) where it's not safe to store a `client_secret` securely.

The main problem PKCE solves is the risk of an attacker intercepting the authorization code returned by the authorization server (e.g., Keycloak) and using it to obtain an access token.

### **Why PKCE is Needed:**

In the **Authorization Code Flow**, the client exchanges an authorization code for an access token. This code is typically sent via the redirect URI after the user successfully authenticates. The original OAuth 2.0 Authorization Code Flow is vulnerable to **authorization code interception**:

1. **Authorization Code Interception**: An attacker intercepts the authorization code from the redirect URI (e.g., through man-in-the-middle attacks or logging) and exchanges it for an access token using the client’s `client_secret`.
2. **No Client Secret on Public Clients**: Public clients like mobile apps or JavaScript-based apps do not have a `client_secret` that can be securely stored, which makes them vulnerable to this kind of attack.

PKCE mitigates this risk by introducing an extra layer of security during the **Authorization Code Flow**. The authorization server (Keycloak) uses **PKCE** to ensure that the entity requesting the token is the same one that initiated the request, even if the authorization code is intercepted.

### **PKCE Flow:**

#### **1. Initiate Authorization Request (with Code Challenge)**

- The client generates a random string called the `code_verifier`.
- The client then creates a `code_challenge` by applying a hash function (SHA256) to the `code_verifier`.
- The `code_challenge` and `code_challenge_method` are included in the authorization request.

Example Authorization URL with PKCE:

```plaintext
https://localhost:8088/realms/example-realm/protocol/openid-connect/auth?response_type=code&client_id=myclient&redirect_uri=http://localhost:3000/callback&code_challenge=sha256_hash_of_code_verifier&code_challenge_method=S256
```

#### **2. User Logs In**

- The user is redirected to Keycloak for authentication.
- After the user successfully logs in, Keycloak redirects back to the `redirect_uri` with an authorization code.

#### **3. Token Request (with Code Verifier)**

- The client sends the authorization code along with the original `code_verifier` to exchange the authorization code for an access token.

Example Token Request:

```bash
curl -X POST "http://localhost:8088/realms/example-realm/protocol/openid-connect/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "grant_type=authorization_code" \
-d "code=authorization_code_here" \
-d "redirect_uri=http://localhost:3000/callback" \
-d "client_id=myclient" \
-d "code_verifier=original_code_verifier_here"
```

#### **4. Token Exchange**

- Keycloak receives the request and hashes the `code_verifier` provided by the client.
- Keycloak compares the `code_verifier` hash with the `code_challenge` hash it received earlier.
- If they match, the token is returned to the client.
- If they don't match, the request is rejected, preventing an attacker from using an intercepted authorization code.

### **PKCE in Keycloak**

Keycloak supports PKCE out of the box for public clients. Here's how to use it:

- Ensure the `code_challenge_method` is supported in your Keycloak client configuration (e.g., setting it to `S256`).
- PKCE is particularly important for **public clients**, like native mobile apps or single-page applications (SPA), where storing the `client_secret` securely is not feasible.

By implementing PKCE, you ensure that only the client that initiated the authentication flow can successfully complete it, significantly improving security for user authentication in mobile, browser-based, and other public clients.


??????????????????????????????
Here's a step-by-step guide for implementing PKCE (Proof Key for Code Exchange) flow using `cURL`, with an example of generating a code verifier and the subsequent requests to authenticate and obtain an access token.

### Step 1: **Generate the Code Verifier and Code Challenge**

#### **Generate Code Verifier**
A **code verifier** is a random string that is used to create a **code challenge**. The code verifier must be a base64-encoded string that is between 43 and 128 characters long.

You can generate the code verifier using a tool like `openssl` or any online tool, but I will show you how to generate it on the command line.

**Generate the Code Verifier** using `openssl`:
```bash
# Generate a random string (code verifier)
openssl rand -base64 32 | tr -d '=' | tr -d '\n' | tr -d '/'
```

Example output (code verifier):
```bash
XFLc8b6QK4l-8gEoH0w8A5vtuT_6E80IUVaWcTvv6bs
```

#### **Generate Code Challenge**
Next, you need to generate the **code challenge** from the code verifier. The code challenge is the hashed value of the code verifier using SHA256.

To generate the code challenge, you can use this command:
```bash
# Generate the code challenge (base64url-encoded SHA256 of code verifier)
echo -n "XFLc8b6QK4l-8gEoH0w8A5vtuT_6E80IUVaWcTvv6bs" | openssl dgst -sha256 -binary | base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n'
```

Example output (code challenge):
```bash
ZGUzYjNkY2FkZDZlNjY2ZjYzNTUzMGJlMzZkNzM0NDEyY2Q4OGEzNzhkZWI1MmM4ZmQxZGQ5ZDEyMjQzM2UyZTQ
```

### Step 2: **Authorization Request**
With the code verifier and challenge in place, you can make a request to your authorization server to start the authentication flow. The client will ask for authorization using the code challenge.

```bash
# Step 1: Authorization Request (User Authorization)
curl -X GET "https://<keycloak-server>/realms/example-realm/protocol/openid-connect/auth" \
  -G \
  --data-urlencode "response_type=code" \
  --data-urlencode "client_id=myclient" \
  --data-urlencode "redirect_uri=http://localhost:8088/callback" \
  --data-urlencode "scope=openid" \
  --data-urlencode "code_challenge_method=S256" \
  --data-urlencode "code_challenge=ZGUzYjNkY2FkZDZlNjY2ZjYzNTUzMGJlMzZkNzM0NDEyY2Q4OGEzNzhkZWI1MmM4ZmQxZGQ5ZDEyMjQzM2UyZTQ"
```

- `response_type=code`: This specifies the authorization code flow.
- `client_id=myclient`: The client ID registered in Keycloak.
- `redirect_uri=http://localhost:8088/callback`: The URI to which the authorization server will send the response (this must match the one registered in the Keycloak client).
- `scope=openid`: The scope of the requested information (OpenID Connect).
- `code_challenge_method=S256`: Specifies that SHA256 will be used to generate the code challenge.
- `code_challenge=<code_challenge>`: The code challenge that was generated in the first step.

When the user authorizes the application, they will be redirected to the provided `redirect_uri` with an authorization code.

### Step 3: **Exchange the Authorization Code for Tokens**

Once the user has authorized the application, Keycloak will redirect them to your redirect URI with an authorization code. You can then use this code to obtain the `access_token` and `id_token`.

```bash
# Step 2: Token Request (Exchange the authorization code for an access token)
curl -X POST "https://<keycloak-server>/realms/example-realm/protocol/openid-connect/token" \
  -d "grant_type=authorization_code" \
  -d "code=<authorization_code>" \
  -d "redirect_uri=http://localhost:8088/callback" \
  -d "client_id=myclient" \
  -d "client_secret=mysecret" \
  -d "code_verifier=XFLc8b6QK4l-8gEoH0w8A5vtuT_6E80IUVaWcTvv6bs"
```

- `grant_type=authorization_code`: This specifies that you're using the authorization code grant type.
- `code=<authorization_code>`: The authorization code received after user authorization.
- `redirect_uri=http://localhost:8088/callback`: The redirect URI registered in Keycloak.
- `client_id=myclient`: The client ID of the application.
- `client_secret=mysecret`: The client secret if the client is confidential (for public clients, omit this).
- `code_verifier=<code_verifier>`: The code verifier used to generate the code challenge.

### Step 4: **Access Tokens and ID Token**

The response will contain the `access_token`, `id_token`, and optionally a `refresh_token`:

```json
{
  "access_token": "<access_token>",
  "expires_in": 3600,
  "token_type": "bearer",
  "id_token": "<id_token>",
  "refresh_token": "<refresh_token>"
}
```

### Step 5: **Use the Access Token**

You can now use the `access_token` to make authenticated requests to your API. Here's an example of a request with the bearer token:

```bash
curl -X GET "https://<your-api-server>/api/protected-endpoint" \
  -H "Authorization: Bearer <access_token>"
```

---

### Best Practices

1. **Code Verifier Length**: Ensure the code verifier is sufficiently random and between 43 to 128 characters long to maintain security.
2. **Secure Storage**: Store the code verifier securely in your frontend (e.g., in memory, not in local storage).
3. **PKCE Enabled**: Always enable PKCE for public clients to mitigate the risk of interception of the authorization code.
4. **Use HTTPS**: Always use HTTPS for secure communication to prevent token interception.
