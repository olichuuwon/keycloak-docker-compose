import requests


# Function to fetch a group by its ID
def get_group_attributes(access_token, realm_name, group_id):
    group_url = (
        f"http://localhost:8080/auth/admin/realms/{realm_name}/groups/{group_id}"
    )
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # Fetch the group by ID
        response = requests.get(group_url, headers=headers)
        response.raise_for_status()
        group_data = response.json()

        print("\nGroup Attributes:")
        print(f"Group Name: {group_data.get('name')}")
        print(f"Group ID: {group_data.get('id')}")
        print(f"Attributes: {group_data.get('attributes')}")

        return group_data
    except requests.RequestException as e:
        print(f"Error fetching group attributes: {e}")
        return None


# Function to get group ID by name
def get_group_id_by_name(access_token, realm_name, group_name):
    groups_url = f"http://localhost:8080/auth/admin/realms/{realm_name}/groups?search={group_name}"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        # Fetch all groups and search for the one with the name
        response = requests.get(groups_url, headers=headers)
        response.raise_for_status()
        groups = response.json()

        # Find the group by name
        for group in groups:
            if group.get("name") == group_name:
                return group.get("id")

        print(f"Group {group_name} not found.")
        return None
    except requests.RequestException as e:
        print(f"Error fetching groups: {e}")
        return None


# Example usage
def main():
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJvUnZiREVXR0RYa21Ud1VVbVJKZ1VoMzlmTFVlc3I0MWcyZC1qTnp4UkUwIn0.eyJleHAiOjE3MzM3Mzg5OTYsImlhdCI6MTczMzczODY5NiwianRpIjoiNGFhZTkzMzQtNmFjNi00NTRiLWJlZjktMTdiOGIxMjZlMTEwIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwL3JlYWxtcy9leGFtcGxlLXJlYWxtIiwic3ViIjoiNzdjZmQ2M2EtM2FmOS00ODU0LWIwYTUtM2FmYjE4NTBmZmUwIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoibXljbGllbnQiLCJzaWQiOiI4NjhiMWNlNC1lYTQ4LTQ5YjAtOGE0Ni0xYjVhODliOTA0NzQiLCJhY3IiOiIwIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODA4MCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsidXNlciJdfSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiVXNlciBHcm91cDFSb2xlQSIsImdyb3VwcyI6WyIvZ3JvdXBfMS9zdWJncm91cF8xYSJdLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJ1c2VyX2dyb3VwXzFfcm9sZV9hIiwiZ2l2ZW5fbmFtZSI6IlVzZXIiLCJmYW1pbHlfbmFtZSI6Ikdyb3VwMVJvbGVBIiwiZW1haWwiOiJ1c2VyX2dyb3VwXzFfcm9sZV9hQGV4YW1wbGUuY29tIn0.ZFDIde-RI4FanzcTr5naMAW_mQwZZzsZCTV5gjC8Ku1m7Hg3TouhnLfLphAcivFs06jXUXkthfqcIqExgLXne4-XXAonqXL6TzZxB02WDfXrkKsLIkBTPXpKeUKkf3hVjvBfzUjogJ2VetKPdBG3TpX16zdDF8qFAbEMsNIBpq-u7ddSxW_0TVKOkJVBnHuThOkOTbMtlg0m_ieTArCvAnJ0COb-E7R6Uuqf74XOM2dKOj0gXQcSSyZPrpwSaYOOYNJzjpjNIvsxl9D1HFqXAvgjIpBYkWq7PHii38gD7WWiWt89y_9r4snFxPp--1cIhNKyz78FVUWiVx3GLch6VQ"  # Replace with a valid access token
    realm_name = "example-realm"
    group_name = "/group_1/subgroup_1a"  # Name of the subgroup to search

    # Step 1: Get the group ID by name
    group_id = get_group_id_by_name(access_token, realm_name, group_name)

    if group_id:
        # Step 2: Fetch and print the group attributes
        get_group_attributes(access_token, realm_name, group_id)


if __name__ == "__main__":
    main()
