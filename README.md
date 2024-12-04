# Keycloak Docker Compose

This guide provides details on running Keycloak with or without PostgreSQL, best practices for configuring realms, roles, groups, and users, and practical examples to simplify development and testing. It also covers how to generate and use JWT tokens for API authentication.

---

## Table of Contents

1. [Day 1: Initial Compose Setup](#day-1-initial-compose-setup)
2. [Day 2: Example API Request](#day-2-example-api-request)

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
      - "8080:8080"
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

### **Role and Group Assignment Example in Keycloak**

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

### **Does the `.env` File Auto-Load?**

Yes, in Docker Compose, the `.env` file is automatically loaded if it is in the same directory as `docker-compose.yml`.

#### **How It Works**

- Variables in `.env` are accessible within `docker-compose.yml` using `${VARIABLE_NAME}` syntax.
- Variables in `.env` take precedence over system-wide variables but can be overridden by values set explicitly in `docker-compose.yml`.

To verify, use:

```bash
docker-compose config
```

For explicit loading, use:

```bash
docker-compose --env-file <your_env_file> up
```

---

## Day 2: Example API Request

### 1. Requesting an Access Token

To obtain an access token, use the following `curl` command to send a POST request to the Keycloak server:

```bash
curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
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
curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
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
curl http://localhost:8080/realms/example-realm/protocol/openid-connect/certs
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
curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"
```

```bash
C:\Users\Jesly>curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
More? -H "Content-Type: application/x-www-form-urlencoded" ^
More? -d "client_id=myclient" ^
More? -d "username=GroupAUser" ^
More? -d "password=groupA123" ^
More? -d "grant_type=password"
{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoQWcwNFV5VTRtdTFZS2o2Q1pVWWpNUDMxTzV3Z2FYUUtZVVUyT2d2anNFIn0.eyJleHAiOjE3MzMyOTA2NTksImlhdCI6MTczMzI5MDM1OSwianRpIjoiYmI5MDI3ZTgtMjUzNC00ODhjLWExZjgtMzAzODhmZTczNGVkIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwic3ViIjoiNWRhNDM4NTktOTVjZi00MDYxLWE0MmMtMDc2MDUyZmU3OWQ0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibXljbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiOGE0ZGQyNmQtZTYzMC00Yzc5LWIxYmItZWY0YjRlZDIwOTgyIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyIxIiwiNSJdfSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiOGE0ZGQyNmQtZTYzMC00Yzc5LWIxYmItZWY0YjRlZDIwOTgyIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInByZWZlcnJlZF91c2VybmFtZSI6Imdyb3VwYXVzZXIifQ.HkeFPtHAEqrXepNuDECFL-wqdtP8m94MLC6y4M2pXS3Ge1tlxerMUFisOjlRdSj2qvnlQ5Za_ZT8hfYLztdoH_dq_wdlVaLHLzMRFjc3D2RZvqjYEc3f_VIHYjDWLCxMxrYani46NjhrAIoEqadXe2BwfHawRl4ZJ6mpw8TkWzDMKMRCBGU2kXvxqCcFw9X4Jq6cLt6iFIFstLfkZpp6y9YCvuPShb9QScHgmCPKqbV3ZTGjX3nr8SJr9xmaA1YAR5nXhX_DElKMprjmkpLMwTUL_R0U1PjtzDVsedz1hiNZF0BxQgjfw2Dol9GxCeno8i9OMRy-rHEFm7FMa6jphw","expires_in":300,"refresh_expires_in":1800,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiMTBjMmY4MC0wN2RmLTQ4YWEtOTU1Yy1jZTNmYTM1OGMyZTQifQ.eyJleHAiOjE3MzMyOTIxNTksImlhdCI6MTczMzI5MDM1OSwianRpIjoiODcxOTg3ZTEtNzdiYS00YzNmLTg5MDEtZDc1MGRmMTQ5OGY2IiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwic3ViIjoiNWRhNDM4NTktOTVjZi00MDYxLWE0MmMtMDc2MDUyZmU3OWQ0IiwidHlwIjoiUmVmcmVzaCIsImF6cCI6Im15Y2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6IjhhNGRkMjZkLWU2MzAtNGM3OS1iMWJiLWVmNGI0ZWQyMDk4MiIsInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsInNpZCI6IjhhNGRkMjZkLWU2MzAtNGM3OS1iMWJiLWVmNGI0ZWQyMDk4MiJ9.f119s3L7r0bdakOLSkIPk5T6waEKP1YV7GwNhLv34tA","token_type":"Bearer","not-before-policy":0,"session_state":"8a4dd26d-e630-4c79-b1bb-ef4b4ed20982","scope":"profile email"}
```

```bash
curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
-H "Content-Type: application/x-www-form-urlencoded" ^
-d "client_id=myclient" ^
-d "client_secret=mysecret" ^
-d "username=GroupAUser" ^
-d "password=groupA123" ^
-d "grant_type=password"

```

```bash
C:\Users\Jesly>curl -X POST "http://localhost:8080/realms/example-realm/protocol/openid-connect/token" ^
More? -H "Content-Type: application/x-www-form-urlencoded" ^
More? -d "client_id=myclient" ^
More? -d "client_secret=mysecret" ^
More? -d "username=GroupAUser" ^
More? -d "password=groupA123" ^
More? -d "grant_type=password"
{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJoQWcwNFV5VTRtdTFZS2o2Q1pVWWpNUDMxTzV3Z2FYUUtZVVUyT2d2anNFIn0.eyJleHAiOjE3MzMyOTIxNTUsImlhdCI6MTczMzI5MTg1NSwianRpIjoiNWQ4ZWY2NTgtMzUwMy00Zjk3LTkyZWQtZmZjMWM3ZDA4ZThjIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwic3ViIjoiNWRhNDM4NTktOTVjZi00MDYxLWE0MmMtMDc2MDUyZmU3OWQ0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibXljbGllbnQiLCJzZXNzaW9uX3N0YXRlIjoiOTg3Y2NhN2QtNjQ4MC00MzZlLTk2MDYtY2U4YjhkNjBjZmI5IiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyIxIiwiNSJdfSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiOTg3Y2NhN2QtNjQ4MC00MzZlLTk2MDYtY2U4YjhkNjBjZmI5IiwiZW1haWxfdmVyaWZpZWQiOnRydWUsInByZWZlcnJlZF91c2VybmFtZSI6Imdyb3VwYXVzZXIifQ.qAHsWBP-o28KuCWArLXX0xDCp7ggx8K_uk2oU9MpuHF7vbmf4u456XgokfTL-Zsf8W2UvDropDFMk6vpaXKSUb0q6UXmv3DGpanIoVjfOfBdMPOjNv-55dAoAaXLgWB8Jwwaauidrja2xS0j6ndsA_usj2CGFU_oDe5N1Cbfk3-68tl2ThAMCEO1orlEYt9E61g-ZQz7YimS_y54mgfi_3DHVtnQcxd0j77pJtlEa2-3Tt4z1Vq-HVxGiy3rxBryW7H0o-GDelNZ7CRkmALpe1VeOmVLrN66UJqTxV-fAJ5_cWTgwZyeDsBwhG4bvPf3mKhVMJOK1SntKlpRv2KE3w","expires_in":300,"refresh_expires_in":1800,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJiMTBjMmY4MC0wN2RmLTQ4YWEtOTU1Yy1jZTNmYTM1OGMyZTQifQ.eyJleHAiOjE3MzMyOTM2NTUsImlhdCI6MTczMzI5MTg1NSwianRpIjoiODZjNTBiM2EtZGYyMS00MDc5LTliOTMtMjk3ZmZkM2JjMDEwIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwiYXVkIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwic3ViIjoiNWRhNDM4NTktOTVjZi00MDYxLWE0MmMtMDc2MDUyZmU3OWQ0IiwidHlwIjoiUmVmcmVzaCIsImF6cCI6Im15Y2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6Ijk4N2NjYTdkLTY0ODAtNDM2ZS05NjA2LWNlOGI4ZDYwY2ZiOSIsInNjb3BlIjoicHJvZmlsZSBlbWFpbCIsInNpZCI6Ijk4N2NjYTdkLTY0ODAtNDM2ZS05NjA2LWNlOGI4ZDYwY2ZiOSJ9.a_S83wZlbglnqMr2NTjIho7TLGg17ukY3G2ivnU_qsY","token_type":"Bearer","not-before-policy":0,"session_state":"987cca7d-6480-436e-9606-ce8b8d60cfb9","scope":"profile email"}
```

```bash
curl http://localhost:8080/realms/example-realm/protocol/openid-connect/certs
```

```bash
C:\Users\Jesly>curl http://localhost:8080/realms/example-realm/protocol/openid-connect/certs
{"keys":[{"kid":"hAg04UyU4mu1YKj6CZUYjMP31O5wgaXQKYUU2OgvjsE","kty":"RSA","alg":"RS256","use":"sig","n":"xpnh36HH2g4D60CazrlXngw60QEe43CqruG6xHC6m7mY9GKXLno6s8pt1FulYv-NNg_GkpECXY5vM8umyJ7mADLev-ujnU3-gC86OHNTAynKIxdxbtOKxS4RYY70MKUkqqrw6CUADJlr3JlPCzD2UD1e2-_QPGmAnanMzdyH-1zWNeWYARq-FXGhhw5629Il_BSi9-tp7Lj9HpUYcbowHEf-B_qPwzP6viORB-dVwi6sOH8F5bfonKj61HyCEjoWU_4Pq-mrbMx31RZ0pQRUkGC-9NC3cSfEv3CFxq-vMAOPGWYigVnNQTRia1ip2PDIH_LD8bOM7jRh6bWb8RAQDw","e":"AQAB","x5c":["MIICqTCCAZECBgGTkCfJijANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDDA1leGFtcGxlLXJlYWxtMB4XDTI0MTIwNDA1MzA0NloXDTM0MTIwNDA1MzIyNlowGDEWMBQGA1UEAwwNZXhhbXBsZS1yZWFsbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMaZ4d+hx9oOA+tAms65V54MOtEBHuNwqq7husRwupu5mPRily56OrPKbdRbpWL/jTYPxpKRAl2ObzPLpsie5gAy3r/ro51N/oAvOjhzUwMpyiMXcW7TisUuEWGO9DClJKqq8OglAAyZa9yZTwsw9lA9Xtvv0DxpgJ2pzM3ch/tc1jXlmAEavhVxoYcOetvSJfwUovfraey4/R6VGHG6MBxH/gf6j8Mz+r4jkQfnVcIurDh/BeW36Jyo+tR8ghI6FlP+D6vpq2zMd9UWdKUEVJBgvvTQt3EnxL9whcavrzADjxlmIoFZzUE0YmtYqdjwyB/yw/GzjO40Yem1m/EQEA8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAlRmlpQu1z8r3FwOn2+qplR7MIU+wZxQZUNF2lm4R7OSldRFtSCyzkJtkE5KcfR/f65bteCq+mYgfi+KcSyaT+acaDAcgJA5ML3+VWhzV4lj4U3FsMeSnk88N4ez+SEuKw5INZ+ZnJVxQ8ih2PnMhPh3oGLhlSYgwbqmEE7AhOeKRjbXqb6zGyamIwjanWRC0qHfpH3J8N7BWUYURSkukhTwvmULM6h1pxcThWPAhYRBMC1Wp92Y4vyR9BMKxxD+1INefUj44vatEblX0GiNjaNS3Mq2NGnM96I4xblOXguRdfKuJ/GRmDE9n3uiz1VuLJ32XX05NCVhtcdholb6N0w=="],"x5t":"IRF70_5_8gxoJix40wOc1rNQq3w","x5t#S256":"atlcCri24QZyYH_fww12sE5srd7r-s4Y8IqVGqtQHoE"},{"kid":"GxHij8i-0ERWYeTpEg-6CQTRurbjcoHSu9qAe2bAE5A","kty":"RSA","alg":"RSA-OAEP","use":"enc","n":"xIagXMKHV8vAXPZ8AamWEg5qILPse4E28rr8Quw1nebGsOsxZFFU6lPOAn4kZmKIkasTR-G8dOSuqlh_trtXhbGOpoxuynRRCZE4UQfSQ5hiGgrMJbvBPXrWXm3cN4tyWRJpURkj18HKdgPI5AAspSi-B6cNmCWseQjvuoZ-m_5EOBEcQMQEmAOH4w8C1ps2oVAs8GAsQgGWo-tC-jdimDqIBUJ0sQ3awvOosQwVJqIJEVTdRs4WyI3nzp_S2Wafns8ALUjEI6Npn9ugdv76vCoZZBqHxvx6xsOTSeAhBDD8m_jlg9d4xT6BX7GmUJ1lOhFiFQLrNporF2SkabDt1w","e":"AQAB","x5c":["MIICqTCCAZECBgGTkCfKbTANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDDA1leGFtcGxlLXJlYWxtMB4XDTI0MTIwNDA1MzA0N1oXDTM0MTIwNDA1MzIyN1owGDEWMBQGA1UEAwwNZXhhbXBsZS1yZWFsbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMSGoFzCh1fLwFz2fAGplhIOaiCz7HuBNvK6/ELsNZ3mxrDrMWRRVOpTzgJ+JGZiiJGrE0fhvHTkrqpYf7a7V4WxjqaMbsp0UQmROFEH0kOYYhoKzCW7wT161l5t3DeLclkSaVEZI9fBynYDyOQALKUovgenDZglrHkI77qGfpv+RDgRHEDEBJgDh+MPAtabNqFQLPBgLEIBlqPrQvo3Ypg6iAVCdLEN2sLzqLEMFSaiCRFU3UbOFsiN586f0tlmn57PAC1IxCOjaZ/boHb++rwqGWQah8b8esbDk0ngIQQw/Jv45YPXeMU+gV+xplCdZToRYhUC6zaaKxdkpGmw7dcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAaIbWxp02o9bWdzvAKMFq6zcbQ14B2zgPtuhpHVkj2bKHBv1Q23JCLybl3O5sZZvS4YtlKJI5DCxY5OiAvA5RiKJmrvcetVYxhQeW1pK2d1I3iBml+KFdPw7MQZqYAfnxsGVC2OqvVfRor+4A+EmvhDxK5nZzo6KbWPAE2wyVPZE+tAofekrAetbltT587kkRDwrozGBJhDHwtbmr6FcrEPOxIwQv1cJP8gdVtGerG34YfpHPXtL4NEgUc8GQgAE0BbPzYhMAf7JFOhMEiZh70mDbC6a6GN1se+SxnmgsppVrtcNGxM7+Oyp6o+1/9OoT0Ih23s7cJBmElKSctXO3LA=="],"x5t":"ask3R8RjUcS0-ponv2ZeCsiqwJI","x5t#S256":"zTtzYUyT5Y0uU8Ph36kuLQrQMpWHC3MaqCBkWzfOTdA"}]}
```

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
    },
    {
      "kid": "GxHij8i-0ERWYeTpEg-6CQTRurbjcoHSu9qAe2bAE5A",
      "kty": "RSA",
      "alg": "RSA-OAEP",
      "use": "enc",
      "n": "xIagXMKHV8vAXPZ8AamWEg5qILPse4E28rr8Quw1nebGsOsxZFFU6lPOAn4kZmKIkasTR-G8dOSuqlh_trtXhbGOpoxuynRRCZE4UQfSQ5hiGgrMJbvBPXrWXm3cN4tyWRJpURkj18HKdgPI5AAspSi-B6cNmCWseQjvuoZ-m_5EOBEcQMQEmAOH4w8C1ps2oVAs8GAsQgGWo-tC-jdimDqIBUJ0sQ3awvOosQwVJqIJEVTdRs4WyI3nzp_S2Wafns8ALUjEI6Npn9ugdv76vCoZZBqHxvx6xsOTSeAhBDD8m_jlg9d4xT6BX7GmUJ1lOhFiFQLrNporF2SkabDt1w",
      "e": "AQAB",
      "x5c": [
        "MIICqTCCAZECBgGTkCfKbTANBgkqhkiG9w0BAQsFADAYMRYwFAYDVQQDDA1leGFtcGxlLXJlYWxtMB4XDTI0MTIwNDA1MzA0N1oXDTM0MTIwNDA1MzIyN1owGDEWMBQGA1UEAwwNZXhhbXBsZS1yZWFsbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMSGoFzCh1fLwFz2fAGplhIOaiCz7HuBNvK6/ELsNZ3mxrDrMWRRVOpTzgJ+JGZiiJGrE0fhvHTkrqpYf7a7V4WxjqaMbsp0UQmROFEH0kOYYhoKzCW7wT161l5t3DeLclkSaVEZI9fBynYDyOQALKUovgenDZglrHkI77qGfpv+RDgRHEDEBJgDh+MPAtabNqFQLPBgLEIBlqPrQvo3Ypg6iAVCdLEN2sLzqLEMFSaiCRFU3UbOFsiN586f0tlmn57PAC1IxCOjaZ/boHb++rwqGWQah8b8esbDk0ngIQQw/Jv45YPXeMU+gV+xplCdZToRYhUC6zaaKxdkpGmw7dcCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAaIbWxp02o9bWdzvAKMFq6zcbQ14B2zgPtuhpHVkj2bKHBv1Q23JCLybl3O5sZZvS4YtlKJI5DCxY5OiAvA5RiKJmrvcetVYxhQeW1pK2d1I3iBml+KFdPw7MQZqYAfnxsGVC2OqvVfRor+4A+EmvhDxK5nZzo6KbWPAE2wyVPZE+tAofekrAetbltT587kkRDwrozGBJhDHwtbmr6FcrEPOxIwQv1cJP8gdVtGerG34YfpHPXtL4NEgUc8GQgAE0BbPzYhMAf7JFOhMEiZh70mDbC6a6GN1se+SxnmgsppVrtcNGxM7+Oyp6o+1/9OoT0Ih23s7cJBmElKSctXO3LA=="
      ],
      "x5t": "ask3R8RjUcS0-ponv2ZeCsiqwJI",
      "x5t#S256": "zTtzYUyT5Y0uU8Ph36kuLQrQMpWHC3MaqCBkWzfOTdA"
    }
  ]
}
```

### 1. **Fetching the JWKS:**

The JWKS (JSON Web Key Set) provides a collection of public keys, typically in **JWK (JSON Web Key) format**, and these keys can be converted to **PEM** format to verify the JWT.

You retrieve the JWKS from an endpoint, typically from an authorization server (like Keycloak). The JWKS contains one or more public keys, each with its own `kid` (key ID), which can be used to match the key to a specific JWT.

For example, a typical JWK might look like this:

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
      ]
    }
  ]
}
```

This JWKS contains an RSA key (denoted by `kty: RSA`), which is used for signing and verifying JWTs. The key has:

- **`n`** (modulus): The RSA public key modulus.
- **`e`** (exponent): The RSA public key exponent.
- **`x5c`** (certificate chain): The X.509 certificate chain, which contains the public key in PEM format.

### 2. **Converting JWK to PEM Format**

To verify a JWT signed with an RSA algorithm (such as RS256), you need to convert the public key (the JWK) into **PEM format**. The PEM format is a base64-encoded representation of the public key, which is typically used for verification purposes.

You can convert the JWK to a PEM format manually or using a library. Here's a general outline of how you can do it:

#### Steps

1. **Extract the Modulus (`n`) and Exponent (`e`)**:
   - These values are provided in the JWKS for each key.
2. **Convert to PEM Format**:
   - Use the modulus (`n`) and exponent (`e`) to create an RSA public key in PEM format.
   - Alternatively, some libraries or tools can do this conversion automatically.

For instance, in Python, you can use the `cryptography` library to convert the `n` and `e` values into an RSA public key object and then export it in PEM format.

Example in Python using `cryptography`:

```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

# Base64 decode 'n' and 'e' from the JWK
n = base64.urlsafe_b64decode("xpnh36HH2g4D60CazrlXngw60QEe43CqruG6xHC6m7mY9GKXLno6s8pt1FulYv-NNg_GkpECXY5vM8umyJ7mADLev-ujnU3-gC86OHNTAynKIxdxbtOKxS4RYY70MKUkqqrw6CUADJlr3JlPCzD2UD1e2-_QPGmAnanMzdyH-1zWNeWYARq-FXGhhw5629Il_BSi9-tp7Lj9HpUYcbowHEf-B_qPwzP6viORB-dVwi6sOH8F5bfonKj61HyCEjoWU_4Pq-mrbMx31RZ0pQRUkGC-9NC3cSfEv3CFxq-vMAOPGWYigVnNQTRia1ip2PDIH_LD8bOM7jRh6bWb8RAQDw")
e = base64.urlsafe_b64decode("AQAB")

# Create the RSA public key
public_key = rsa.RSAPublicNumbers(
    int.from_bytes(n, byteorder='big'),
    int.from_bytes(e, byteorder='big')
).public_key()

# Export the public key in PEM format
pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print(pem.decode('utf-8'))
```

This will output the PEM-formatted public key, which can be used to verify JWT signatures.

### 3. **Verifying JWT Signature Using PEM**

Once you have the public key in PEM format, you can use it to verify the JWT's signature. Here's how it works:

1. The JWT is received, and its header is decoded.
2. The `kid` (Key ID) in the JWT header is used to find the corresponding public key in the JWKS.
3. The public key is converted to PEM format.
4. The JWT's signature is verified using the **RS256** algorithm and the PEM-formatted public key.

### 4. **Using the PEM to Verify JWT Signature**

Libraries like `pyjwt` (Python) or `jsonwebtoken` (Node.js) automatically handle the process of fetching the JWKS, matching the `kid`, converting the JWK to PEM, and verifying the JWT signature. Here's an example of how to verify the JWT with the PEM:

Here’s the continuation of the Python example using `pyjwt` to verify the JWT signature with the PEM public key:

### Python Example using `pyjwt` to Verify JWT

```python
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Load the PEM public key (either from JWKS or a file)
with open('public_key.pem', 'r') as pem_file:
    pem_key = pem_file.read()

# Load the JWT token (replace with your actual token)
jwt_token = "your.jwt.token"

# Verify the JWT signature using RS256 algorithm and PEM public key
try:
    decoded_token = jwt.decode(jwt_token, pem_key, algorithms=["RS256"])
    print("JWT decoded and verified successfully:")
    print(decoded_token)
except jwt.ExpiredSignatureError:
    print("The token has expired.")
except jwt.JWTClaimsError:
    print("Invalid claims in the token.")
except Exception as e:
    print(f"Error decoding token: {e}")
```

### Steps Explained

1. **Loading the PEM Key**:
   - The PEM key (which could be manually retrieved or generated from JWKS) is read from a file in this example. You can also retrieve it from a JWKS endpoint programmatically if needed.
2. **JWT Token**:
   - Replace `jwt_token` with the actual JWT that you want to verify.
3. **Verifying the JWT**:
   - The `jwt.decode` method verifies the JWT’s signature using the **RS256** algorithm and the PEM key. If the token is valid and the signature matches, it will return the decoded token. If the token is invalid, it will raise appropriate exceptions.

### Example Output

If the JWT is valid:

```bash
JWT decoded and verified successfully:
{'sub': 'user123', 'name': 'John Doe', 'iat': 1616580401}
```

If the token is expired or invalid:

```bash
The token has expired.
```

Or if there is any other error in decoding the token:

```bash
Error decoding token: <error_message>
```

### Conclusion

To summarize, here’s how the JWKS is used to verify the JWT:

- **JWKS** contains public keys in JWK format.
- The JWT contains a `kid` (key ID) in the header, which helps match the key to the appropriate key in the JWKS.
- The corresponding JWK is converted into a **PEM format** public key.
- The **PEM public key** is used to verify the JWT’s signature to ensure its authenticity.

By using **JWKS** and the public key in PEM format, you can securely verify JWTs without needing to share or store secrets between your application and Keycloak. This method is secure, scalable, and recommended for handling public-key signatures in JWT-based authentication.
