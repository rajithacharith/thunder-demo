# Thunder File Mount Synchronization

Automated GitHub Action workflow that synchronizes YAML configuration files from the repository to Choreo file mounts.

## Overview

This workflow automatically:
- Detects changes to YAML files in the `resources/` directory
- Creates/updates ConfigMaps in Choreo
- Mounts files to containers at `/opt/thunder/repository/resources/<path>`
- Handles file additions, modifications, renames, and deletions

## File Mapping

Local files in the repository are mounted to the following paths in Choreo containers:

```
resources/applications/application_1.yaml
  → /opt/thunder/repository/resources/applications/application_1.yaml

resources/flows/auth-flow-wso2-cloud.yaml
  → /opt/thunder/repository/resources/flows/auth-flow-wso2-cloud.yaml

resources/identity_providers/github_idp.yaml
  → /opt/thunder/repository/resources/identity_providers/github_idp.yaml

... and so on
```

## Setup Instructions

### 1. Configure GitHub Repository Variables

Go to your repository → Settings → Secrets and variables → Actions → Variables

Add the following **Repository Variables**:

| Variable Name | Description | Example |
|---------------|-------------|---------|
| `BASE_URL` | Choreo API base URL | `https://apis.choreo.dev/devops/1.0.0` |
| `ORG_UUID` | Organization UUID | `abc-123-def-456` |
| `PROJECT_ID` | Project ID | `project-789` |
| `COMPONENT_ID` | Component ID | `component-xyz` |
| `ENV_ID` | Environment ID | `env-123` |
| `APP_ENV_ID` | App Environment ID | `app-env-456` |

### 2. Configure GitHub Repository Secrets

Go to your repository → Settings → Secrets and variables → Actions → Secrets

Add the following **Repository Secret**:

| Secret Name | Description |
|-------------|-------------|
| `ACCESS_TOKEN` | Choreo API access token |

### 3. Create Resources Branch

The workflow triggers on pushes to the `resources` branch:

```bash
# Create and push the resources branch
git checkout -b resources
git push -u origin resources
```

## How It Works

### Trigger Conditions

The workflow runs when:
- Changes are pushed to the `resources` branch
- Changes affect files matching `resources/**/*.yaml`

### Sync Process

1. **Detect Changes**
   - Uses `git diff` to identify added, modified, renamed, or deleted files
   - Only processes files in the `resources/` directory

2. **Fetch Current State**
   - Retrieves all containers for the release
   - Retrieves all existing ConfigMaps
   - Retrieves existing mounts for each container

3. **Sync Operations**
   - **Added/Modified Files**: 
     - Creates ConfigMap (if new) or updates existing ConfigMap (if content changed)
     - Creates file mounts on all containers (if not present)
   - **Renamed Files**: 
     - Deletes old mounts
     - Updates mount path to new location
   - **Deleted Files**: 
     - Removes mounts from all containers
     - Deletes ConfigMap

4. **Report Results**
   - Displays summary of successful and failed operations
   - Uploads detailed logs as workflow artifacts

## Usage Examples

### Adding a New Configuration File

1. Create your YAML file in the appropriate subdirectory:
   ```bash
   # Example: Add a new application
   cat > resources/applications/my_app.yaml << EOF
   id: "new-app-id"
   name: "My Application"
   description: "My new app"
   EOF
   ```

2. Commit and push to the `resources` branch:
   ```bash
   git add resources/applications/my_app.yaml
   git commit -m "Add new application configuration"
   git push origin resources
   ```

3. The workflow will automatically:
   - Create ConfigMap: `thunder-applications-my_app`
   - Mount to: `/opt/thunder/repository/resources/applications/my_app.yaml`
   - Deploy changes to all containers

### Modifying an Existing File

1. Edit the file:
   ```bash
   vim resources/identity_providers/github_idp.yaml
   ```

2. Commit and push:
   ```bash
   git add resources/identity_providers/github_idp.yaml
   git commit -m "Update GitHub IDP configuration"
   git push origin resources
   ```

3. The workflow will:
   - Detect content change via SHA256 hash comparison
   - Update the existing ConfigMap with new content
   - Redeploy containers automatically

### Renaming a File

1. Rename using git:
   ```bash
   git mv resources/applications/old_name.yaml resources/applications/new_name.yaml
   git commit -m "Rename application config"
   git push origin resources
   ```

2. The workflow will:
   - Delete the old mount path
   - Create new mount with updated path
   - Update ConfigMap name accordingly

### Deleting a File

1. Delete and commit:
   ```bash
   git rm resources/flows/unused_flow.yaml
   git commit -m "Remove unused flow"
   git push origin resources
   ```

2. The workflow will:
   - Remove all mounts from containers
   - Delete the ConfigMap from Choreo

## ConfigMap Naming Convention

ConfigMaps are named using the pattern: `thunder-<directory>-<filename>`

Examples:
```
resources/applications/application_1.yaml
  → ConfigMap: thunder-applications-application_1

resources/identity_providers/github_idp.yaml
  → ConfigMap: thunder-identity_providers-github_idp

resources/flows/auth-flow-wso2-cloud.yaml
  → ConfigMap: thunder-flows-auth-flow-wso2-cloud
```

## Monitoring and Troubleshooting

### View Workflow Runs

1. Go to **Actions** tab in your repository
2. Select **Sync File Mounts to Choreo** workflow
3. Click on a specific run to see details

### Check Logs

The workflow provides detailed logs with emojis for easy scanning:
- 🚀 Workflow start
- 📋 File changes detected
- 📡 Fetching Choreo state
- 🔄 Processing files
- ✓ Successful operations
- ❌ Failed operations
- 📊 Final summary

### Common Issues

**Issue**: "Missing required environment variables"
- **Solution**: Verify all repository variables and secrets are configured

**Issue**: "HTTP 401 Unauthorized"
- **Solution**: Check that `ACCESS_TOKEN` secret is valid and not expired

**Issue**: "HTTP 404 Not Found"
- **Solution**: Verify that `COMPONENT_ID`, `ENV_ID`, and `APP_ENV_ID` are correct

**Issue**: No changes detected
- **Solution**: Ensure changes are in `resources/**/*.yaml` and pushed to `resources` branch

## File Structure

```
.
├── .github/
│   └── workflows/
│       └── sync-file-mounts.yml          # GitHub Action workflow
├── scripts/
│   └── sync_file_mounts.py              # Python sync script
├── resources/
│   ├── applications/                    # Application configs
│   ├── flows/                          # Authentication flows
│   ├── identity_providers/             # IDP configurations
│   ├── organization_units/             # Organization units
│   └── user_schemas/                   # User schema definitions
└── README_FILE_MOUNTS.md               # This file
```

## Advanced Configuration

### Change Mount Permissions

By default, files are mounted with `0644` permissions (read/write for owner, read-only for group/others).

To change this, edit `scripts/sync_file_mounts.py`:

```python
def create_config_mount(self, container_id: str, configmap_id: str, mount_path: str) -> None:
    payload = {
        # ...
        'mount_permissions': '0600',  # Change to desired permissions
        # ...
    }
```

### Disable Automatic Deployment

By default, changes trigger automatic deployment (`deploy_changes: true`).

To disable, edit `scripts/sync_file_mounts.py`:

```python
def create_config_mount(self, container_id: str, configmap_id: str, mount_path: str) -> None:
    payload = {
        # ...
        'deploy_changes': False,  # Set to False
        # ...
    }
```

### Change Base Reference for Diff

By default, the workflow compares against the previous commit (`HEAD^`).

To compare against a different reference, edit `.github/workflows/sync-file-mounts.yml`:

```yaml
- name: Run file mount synchronization
  env:
    BASE_REF: 'origin/main'  # Compare against main branch
    # ... other env vars
```

## Security Considerations

- **Access Token**: Keep `ACCESS_TOKEN` secret and rotate regularly
- **File Permissions**: Review mount permissions based on sensitivity
- **Branch Protection**: Consider protecting the `resources` branch with required reviews
- **Audit Logs**: Review workflow run logs regularly for unauthorized changes

## API Reference

This workflow uses the Choreo DevOps API. For complete API documentation, see:
- [FILE_MOUNT_API_REFERENCE.md](FILE_MOUNT_API_REFERENCE.md)

## Contributing

When adding new resource types:

1. Create subdirectory under `resources/`
2. Add YAML files following existing patterns
3. Push to `resources` branch
4. Verify mounts are created correctly

## Support

For issues or questions:
1. Check workflow logs in the Actions tab
2. Review this documentation
3. Consult the API reference
4. Contact the DevOps team

---

**Last Updated**: December 22, 2025  
**Version**: 1.0.0
