# Keycloak Docker Compose Setup

This guide provides details on running Keycloak with or without PostgreSQL, best practices for configuring realms, roles, groups, and users, and practical examples to simplify development and testing.

---

## **When You Can Skip PostgreSQL**

You may skip PostgreSQL in the following scenarios:
- **Local Testing or Development**: When testing Keycloak configurations, realms, roles, groups, or authentication flows.
- **Stateless Testing**: If persistence of data between Keycloak restarts is unnecessary.

---

## **Running Keycloak Without PostgreSQL**

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

### **Limitations of H2 Database**
- **No Persistence**: Data is lost when the Keycloak container stops.
- **Performance**: Not optimized for concurrent access or large-scale data.
- **Not Production-Ready**: Avoid using H2 in production environments.

---


## **Keycloak Best Practices**

### **1. Realm Design**
- Use a **single realm** for related applications to simplify management.
- For **multi-tenant systems**, use separate realms per tenant to isolate users and configurations.

### **2. Roles**
- **Realm Roles**: For permissions that span across all clients in the realm (e.g., `admin`, `user`).
- **Client Roles**: For permissions specific to a client (e.g., `editor` for a specific app).
- Use meaningful, descriptive names (e.g., `reader`, `editor`, `admin`).

### **3. Groups**
- Define groups for logical or organizational units (e.g., Engineering, HR).
- Use **group attributes** for metadata (e.g., `department`, `region`).
- Assign roles to groups and add users to groups—minimizing direct role assignments to users.

### **4. User Management**
- Use groups to manage user permissions collectively.
- Avoid assigning roles directly to users unless absolutely necessary.

### **5. Client Configuration**
- Secure clients with appropriate access types (e.g., **confidential** or **public**).
- Use **client scopes** to manage permissions and claims effectively.

### **6. Security**
- Enable **TLS** for Keycloak, especially in production.
- Use strong admin credentials and limit access to the admin console.
- Regularly update Keycloak to benefit from security patches.
- Enable **audit logging** to monitor administrative and authentication events.

### **7. Data Backup and Migration**
- Regularly back up your database (PostgreSQL or H2 for testing).
- Use realm export/import features for managing configurations and migrations.

### **8. Automation**
- Automate provisioning of users, groups, and roles using Keycloak's Admin REST API.
- Maintain JSON or script-based configurations for reproducibility.

### **9. Testing Environments**
- Use the embedded H2 database for lightweight testing.
- Match production configurations in staging environments for validation.

### **10. Monitoring and Scaling**
- Integrate with monitoring tools (e.g., Prometheus, Grafana).
- Plan for scaling by deploying Keycloak in a clustered environment with a load balancer.

---

## **Role and Group Assignment Example in Keycloak**

### Create Realm Roles
1. Navigate to **Roles** in the admin console.
2. Add roles `1`, `2`, `3`, `4`, and `5`.

### Create Groups
1. Navigate to **Groups** in the admin console.
2. Create groups `A`, `B`, and `C`.

### Assign Roles to Group A
1. Select **Group A** → **Role Mappings**.
2. Assign roles `1` and `5`.

### Add Users to Groups
1. Navigate to **Users** → Select a user → **Groups** tab.
2. Add the user to groups `A`, `B`, or `C`.

---

## **Multi-Realm JSON Example**

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
    ]
  }
]

```

---

## **Does the `.env` File Auto-Load?**

Yes, in Docker Compose, the `.env` file is automatically loaded if it is in the same directory as `docker-compose.yml`.

### **How It Works**
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
