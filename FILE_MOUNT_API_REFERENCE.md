# Choreo File Mount API Reference

Complete curl command reference for managing file mounts in Choreo components.

---

## Table of Contents
- [Environment Variables](#environment-variables)
- [Read Operations](#read-operations)
- [Create Operations](#create-operations)
- [Update Operations](#update-operations)
- [Delete Operations](#delete-operations)
- [Complete Workflow Examples](#complete-workflow-examples)

---

## Environment Variables

```bash
# Base configuration
BASE_URL="https://apis.choreo.dev/devops/1.0.0"  # Production
# BASE_URL="https://apis.st.choreo.dev/devops/1.0.0"  # Staging
# BASE_URL="https://apis.preview-dv.choreo.dev/devops/1.0.0"  # Preview

ACCESS_TOKEN="your_access_token_here"
ORG_ID="your_org_id"
ORG_UUID="your_org_uuid"
PROJECT_ID="your_project_id"
COMPONENT_ID="your_component_id"
ENV_ID="your_environment_id"
APP_ENV_ID="your_app_environment_id"
```

---

## Read Operations

### 1. Get Release Containers
*Required first to identify container IDs for mounting configs*

```bash
curl -X GET \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

**Response Structure:**
```json
{
  "data": {
    "containers": [
      {
        "id": "container_id_here",
        "name": "container_name"
      }
    ]
  }
}
```

---

### 2. Get Config Mounts (List existing mounts)

```bash
curl -X GET \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

**Response Structure:**
```json
{
  "data": [
    {
      "id": "mount_id_here",
      "configmap_id": "configmap_id or null",
      "secret_id": "secret_id or null",
      "mount_path": "/app/config.json",
      "mount_type": "File",
      "mount_permissions": "0644",
      "config_key": "data",
      "app_environment_id": "env_id"
    }
  ]
}
```

---

### 3. Get ConfigMap List

```bash
curl -X GET \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

**Response Structure:**
```json
{
  "data": [
    {
      "id": "configmap_id",
      "name": "my-config",
      "config_type": "File",
      "environment_id": "env_id",
      "app_environment_id": "app_env_id",
      "created_at": "2025-12-22T10:00:00Z",
      "updated_at": "2025-12-22T10:00:00Z"
    }
  ]
}
```

---

### 4. Get Secrets List

```bash
curl -X GET \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

---

### 5. Get ConfigMap Details

```bash
CONFIG_MAP_ID="your_configmap_id"

curl -X GET \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap/${CONFIG_MAP_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

**Response Structure:**
```json
{
  "data": {
    "id": "configmap_id",
    "name": "my-config",
    "config_type": "File",
    "data": {
      "data": "file content here"
    },
    "environment_id": "env_id",
    "app_environment_id": "app_env_id"
  }
}
```

---

### 6. Get Secret Details

```bash
SECRET_ID="your_secret_id"

curl -X GET \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret/${SECRET_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

---

## Create Operations

### 1. Create ConfigMap (File Mount)

```bash
curl -X POST \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "config_type": "File",
    "data": {
      "data": "your_file_content_here"
    },
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "my-config-file",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false
  }'
```

**Response Structure:**
```json
{
  "data": {
    "id": "configmap_id_here",
    "name": "my-config-file",
    "config_type": "File"
  }
}
```

---

### 2. Create Secret (File Mount)

```bash
curl -X POST \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "config_type": "File",
    "data": {
      "data": "your_secret_file_content_here"
    },
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "my-secret-file",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false,
    "save_type": "Save",
    "secret_type": "Opaque"
  }'
```

---

### 3. Create Config Mount (File Mount)
*Must be done for each container returned from Get Release Containers*

**For ConfigMap-based File Mount:**
```bash
CONTAINER_ID="container_id_from_step_1"
CONFIG_MAP_ID="configmap_id_from_create"

curl -X POST \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "app_environment_id": "'${APP_ENV_ID}'",
    "config_key": "data",
    "configmap_id": "'${CONFIG_MAP_ID}'",
    "container_id": "'${CONTAINER_ID}'",
    "deploy_changes": true,
    "mount_path": "/app/config.json",
    "mount_permissions": "0644",
    "mount_type": "File",
    "secret_id": null
  }'
```

**For Secret-based File Mount:**
```bash
SECRET_ID="secret_id_from_create"

curl -X POST \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "app_environment_id": "'${APP_ENV_ID}'",
    "config_key": "data",
    "configmap_id": null,
    "container_id": "'${CONTAINER_ID}'",
    "deploy_changes": true,
    "mount_path": "/app/secrets.json",
    "mount_permissions": "0644",
    "mount_type": "File",
    "secret_id": "'${SECRET_ID}'"
  }'
```

---

## Update Operations

### 1. Update ConfigMap (File Mount Content)

**Note:** The current CLI implementation doesn't include update operations. Based on REST API patterns, updates would typically use PUT or PATCH methods with the same endpoint structure as GET operations.

**Expected Pattern (to be verified with API documentation):**

```bash
CONFIG_MAP_ID="your_configmap_id"

curl -X PUT \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap/${CONFIG_MAP_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "config_type": "File",
    "data": {
      "data": "updated_file_content_here"
    },
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "my-config-file",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false
  }'
```

---

### 2. Update Secret (File Mount Content)

```bash
SECRET_ID="your_secret_id"

curl -X PUT \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret/${SECRET_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "config_type": "File",
    "data": {
      "data": "updated_secret_content_here"
    },
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "my-secret-file",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false,
    "save_type": "Save",
    "secret_type": "Opaque"
  }'
```

---

### 3. Update Config Mount (Change Mount Path or Permissions)

**Option A: Delete and Recreate**
Currently implemented approach:
1. Delete the existing mount using DELETE operation
2. Create a new mount with updated parameters

**Option B: Update in Place (Expected Pattern)**

```bash
CONFIG_MOUNT_ID="your_mount_id"

curl -X PUT \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount/${CONFIG_MOUNT_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI" \
  -d '{
    "app_environment_id": "'${APP_ENV_ID}'",
    "config_key": "data",
    "configmap_id": "'${CONFIG_MAP_ID}'",
    "container_id": "'${CONTAINER_ID}'",
    "deploy_changes": true,
    "mount_path": "/app/new-config-path.json",
    "mount_permissions": "0600",
    "mount_type": "File",
    "secret_id": null
  }'
```

---

## Delete Operations

### 1. Delete Config Mount

```bash
CONFIG_MOUNT_ID="mount_id_here"

curl -X DELETE \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount/${CONFIG_MOUNT_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

---

### 2. Delete ConfigMap

**Expected Pattern:**
```bash
CONFIG_MAP_ID="your_configmap_id"

curl -X DELETE \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap/${CONFIG_MAP_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

---

### 3. Delete Secret

**Expected Pattern:**
```bash
SECRET_ID="your_secret_id"

curl -X DELETE \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret/${SECRET_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/plain, */*" \
  -H "User-Agent: Choreo CLI"
```

---

## Complete Workflow Examples

### Example 1: Create a New File Mount (ConfigMap)

```bash
#!/bin/bash

set -e  # Exit on error

# Configuration
BASE_URL="https://apis.choreo.dev/devops/1.0.0"
ACCESS_TOKEN="your_token"
ORG_ID="org_id"
ORG_UUID="org_uuid"
PROJECT_ID="project_id"
COMPONENT_ID="component_id"
ENV_ID="env_id"
APP_ENV_ID="app_env_id"

echo "Step 1: Getting release containers..."
CONTAINERS=$(curl -s -X GET \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json")

echo "Step 2: Creating ConfigMap with file content..."
CONFIG_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config_type": "File",
    "data": {"data": "# Application Configuration\napp_name: MyApp\nversion: 1.0.0"},
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "app-config",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false
  }')

CONFIG_ID=$(echo $CONFIG_RESPONSE | jq -r '.data.id')
echo "Created ConfigMap: $CONFIG_ID"

echo "Step 3: Creating mount for each container..."
for CONTAINER_ID in $(echo $CONTAINERS | jq -r '.data.containers[].id'); do
  echo "  Mounting to container: $CONTAINER_ID"
  curl -s -X POST \
    "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "app_environment_id": "'${APP_ENV_ID}'",
      "config_key": "data",
      "configmap_id": "'${CONFIG_ID}'",
      "container_id": "'${CONTAINER_ID}'",
      "deploy_changes": true,
      "mount_path": "/app/config.yaml",
      "mount_permissions": "0644",
      "mount_type": "File",
      "secret_id": null
    }'
done

echo "File mount created successfully!"
```

---

### Example 2: Update File Mount Content (Delete & Recreate Approach)

```bash
#!/bin/bash

set -e

# Assuming you have the IDs from previous operations
CONFIG_MAP_ID="existing_configmap_id"
MOUNT_ID="existing_mount_id"
CONTAINER_ID="container_id"

echo "Step 1: Deleting existing mount..."
curl -X DELETE \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount/${MOUNT_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"

echo "Step 2: Updating ConfigMap content..."
# Note: Use PUT if update endpoint is available, otherwise delete and recreate
curl -X PUT \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/configmap/${CONFIG_MAP_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config_type": "File",
    "data": {"data": "# Updated Configuration\napp_name: MyApp\nversion: 2.0.0"},
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "app-config",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false
  }'

echo "Step 3: Recreating mount..."
curl -X POST \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "app_environment_id": "'${APP_ENV_ID}'",
    "config_key": "data",
    "configmap_id": "'${CONFIG_MAP_ID}'",
    "container_id": "'${CONTAINER_ID}'",
    "deploy_changes": true,
    "mount_path": "/app/config.yaml",
    "mount_permissions": "0644",
    "mount_type": "File",
    "secret_id": null
  }'

echo "File mount updated successfully!"
```

---

### Example 3: Create Secret-based File Mount

```bash
#!/bin/bash

set -e

echo "Creating secret with sensitive file content..."
SECRET_RESPONSE=$(curl -s -X POST \
  "${BASE_URL}/api/v1/environments/${ENV_ID}/secret?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "config_type": "File",
    "data": {
      "data": "{\n  \"api_key\": \"secret123\",\n  \"db_password\": \"pass456\"\n}"
    },
    "environment_id": "'${ENV_ID}'",
    "metadata": {},
    "name": "app-secrets",
    "organization_id": "'${ORG_UUID}'",
    "project_id": "'${PROJECT_ID}'",
    "app_environment_id": "'${APP_ENV_ID}'",
    "isBase64": false,
    "save_type": "Save",
    "secret_type": "Opaque"
  }')

SECRET_ID=$(echo $SECRET_RESPONSE | jq -r '.data.id')

# Get containers and create mounts
CONTAINERS=$(curl -s -X GET \
  "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json")

for CONTAINER_ID in $(echo $CONTAINERS | jq -r '.data.containers[].id'); do
  curl -s -X POST \
    "${BASE_URL}/api/v1/components/${COMPONENT_ID}/release/${APP_ENV_ID}/container/${CONTAINER_ID}/config-mount?organization_id=${ORG_UUID}&project_id=${PROJECT_ID}" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
      "app_environment_id": "'${APP_ENV_ID}'",
      "config_key": "data",
      "configmap_id": null,
      "container_id": "'${CONTAINER_ID}'",
      "deploy_changes": true,
      "mount_path": "/app/secrets.json",
      "mount_permissions": "0600",
      "mount_type": "File",
      "secret_id": "'${SECRET_ID}'"
    }'
done

echo "Secret file mount created successfully!"
```

---

## Key Parameters Reference

### ConfigMap/Secret Creation (File Type)

| Parameter | Value | Required | Description |
|-----------|-------|----------|-------------|
| `config_type` | `"File"` | Yes | Indicates file-based configuration |
| `data.data` | `string` | Yes | The actual file content |
| `name` | `string` | Yes | Human-readable name for the config |
| `environment_id` | `string` | Yes | Environment UUID |
| `app_environment_id` | `string` | Yes | Application environment UUID |
| `organization_id` | `string` | Yes | Organization UUID |
| `project_id` | `string` | Yes | Project UUID |
| `isBase64` | `boolean` | Yes | Whether content is base64 encoded |
| `metadata` | `object` | Yes | Additional metadata (can be empty) |

### Secret-specific Parameters

| Parameter | Value | Required | Description |
|-----------|-------|----------|-------------|
| `save_type` | `"Save"` | Yes | Save operation type |
| `secret_type` | `"Opaque"` | Yes | Kubernetes secret type |

### Config Mount Creation (File Type)

| Parameter | Value | Required | Description |
|-----------|-------|----------|-------------|
| `mount_type` | `"File"` | Yes | Indicates file mount type |
| `mount_path` | `string` | Yes | Full path where file will be mounted (e.g., `/app/config.json`) |
| `mount_permissions` | `"0644"` or `"0600"` | Yes | Unix file permissions |
| `config_key` | `"data"` | Yes | Field name to extract from config |
| `configmap_id` | `string` or `null` | Yes | ConfigMap ID (null if using secret) |
| `secret_id` | `string` or `null` | Yes | Secret ID (null if using configmap) |
| `container_id` | `string` | Yes | Container UUID |
| `app_environment_id` | `string` | Yes | Application environment UUID |
| `deploy_changes` | `boolean` | Yes | Trigger deployment after mount (typically `true`) |

---

## Notes

1. **Authentication**: All requests require a valid Bearer token in the Authorization header
2. **Container Iteration**: File mounts must be created for each container in the release
3. **Deploy Changes**: Setting `deploy_changes: true` triggers automatic deployment
4. **Update Operations**: The current CLI doesn't implement update endpoints. Updates typically require:
   - For content: Update the ConfigMap/Secret, which automatically reflects in mounted files
   - For mount details: Delete and recreate the mount, or use PUT/PATCH if available
5. **File Permissions**: 
   - `0644`: Read/write for owner, read for group/others (standard config files)
   - `0600`: Read/write for owner only (sensitive files)
6. **Base64 Encoding**: Set `isBase64: true` if content is base64-encoded

---

## Related CLI Commands

```bash
# List configurations
choreo config list --component <name> --env <environment>

# Describe a configuration
choreo config describe --component <name> --env <environment> --config <name>

# Create a file mount configuration
choreo config create --component <name> --env <environment> \
  --name <config-name> --type config-map --mount-type "file mount" \
  --file-content "$(cat config.json)" --file-path "/app/config.json"

# Delete a configuration
choreo config delete --component <name> --env <environment> --config <name>
```

---

## Source Code References

- ConfigMap/Secret operations: `pkg/api/devops/devops-client.go`
- Config creation logic: `internal/cmd/common/config.go` (`CreateConfig` function)
- Delete operations: `internal/cmd/common/config.go` (`DeleteConfigMount` function)
