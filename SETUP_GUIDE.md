# GitHub Configuration Setup Guide

## Quick Setup Checklist

### Step 1: Add Repository Variables

Navigate to: **Repository → Settings → Secrets and variables → Actions → Variables tab**

Click **"New repository variable"** for each:

```
Variable name: BASE_URL
Value: https://apis.choreo.dev/devops/1.0.0
```

```
Variable name: ORG_UUID
Value: [your organization UUID]
```

```
Variable name: PROJECT_ID
Value: [your project ID]
```

```
Variable name: COMPONENT_ID
Value: [your component ID]
```

```
Variable name: ENV_ID
Value: [your environment ID]
```

```
Variable name: APP_ENV_ID
Value: [your app environment ID]
```

### Step 2: Add Repository Secret

Navigate to: **Repository → Settings → Secrets and variables → Actions → Secrets tab**

Click **"New repository secret"**:

```
Secret name: ACCESS_TOKEN
Value: [your Choreo API access token]
```

### Step 3: Create Resources Branch

```bash
git checkout -b resources
git push -u origin resources
```

## Finding Your Choreo IDs

### Option 1: Using Choreo Web Console

1. **Organization UUID**:
   - Go to Choreo Console
   - Check URL: `https://console.choreo.dev/org/{ORG_UUID}/...`

2. **Project ID**:
   - Open your project
   - Check URL: `https://console.choreo.dev/org/{ORG}/projects/{PROJECT_ID}/...`

3. **Component ID**:
   - Open your component
   - Check URL or component details

4. **Environment IDs**:
   - Navigate to component environments
   - Check environment settings/details

### Option 2: Using Choreo CLI

```bash
# List organizations
choreo org list

# List projects
choreo project list

# List components
choreo component list --project <project-name>

# List environments
choreo env list --component <component-name>
```

### Option 3: Using API Calls

If you have an access token, you can query the API:

```bash
# Example: List components
curl -X GET "https://apis.choreo.dev/devops/1.0.0/api/v1/components?organization_id={ORG_UUID}&project_id={PROJECT_ID}" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

## Getting an Access Token

### Using Choreo CLI

```bash
# Login
choreo login

# Get token (stored in ~/.choreo/config.yaml)
cat ~/.choreo/config.yaml | grep token
```

### Using OAuth Flow

1. Go to Choreo Console
2. Navigate to Settings → Access Tokens
3. Generate a new token with required scopes
4. Copy and save securely

## Environment Examples

### Production
```
BASE_URL=https://apis.choreo.dev/devops/1.0.0
```

### Staging
```
BASE_URL=https://apis.st.choreo.dev/devops/1.0.0
```

### Preview
```
BASE_URL=https://apis.preview-dv.choreo.dev/devops/1.0.0
```

## Testing Configuration

### Local Test (Before GitHub Action)

1. Set environment variables locally:

```bash
export BASE_URL='https://apis.choreo.dev/devops/1.0.0'
export ACCESS_TOKEN='your_token'
export ORG_UUID='your_org_uuid'
export PROJECT_ID='your_project_id'
export COMPONENT_ID='your_component_id'
export ENV_ID='your_env_id'
export APP_ENV_ID='your_app_env_id'
```

2. Run the test script:

```bash
./scripts/test-sync.sh
```

3. Verify it works before pushing to GitHub

### Verify GitHub Configuration

After setting up variables/secrets in GitHub:

1. Go to **Actions** tab
2. Click **"Sync File Mounts to Choreo"**
3. Click **"Run workflow"** → Select `resources` branch → **"Run workflow"**
4. Watch the logs to verify configuration

## Security Best Practices

### Access Token Management

- ✅ Store as GitHub Secret (never as Variable)
- ✅ Use tokens with minimal required scopes
- ✅ Rotate tokens regularly (e.g., every 90 days)
- ✅ Use separate tokens for different environments
- ❌ Never commit tokens to repository
- ❌ Never expose tokens in logs

### Branch Protection

Consider protecting the `resources` branch:

1. Go to **Settings → Branches**
2. Add branch protection rule for `resources`
3. Enable:
   - Require pull request reviews
   - Require status checks to pass
   - Require signed commits (optional)

### Audit Trail

- Review workflow runs regularly
- Enable GitHub Advanced Security (if available)
- Monitor Choreo audit logs for API access

## Troubleshooting Configuration Issues

### "Missing required environment variables"

Check that all 7 variables/secrets are configured:
```bash
# Variables (6):
BASE_URL, ORG_UUID, PROJECT_ID, COMPONENT_ID, ENV_ID, APP_ENV_ID

# Secrets (1):
ACCESS_TOKEN
```

### "HTTP 401 Unauthorized"

- Verify `ACCESS_TOKEN` is correct
- Check token hasn't expired
- Ensure token has required scopes/permissions

### "HTTP 404 Not Found"

- Verify all IDs (ORG_UUID, PROJECT_ID, etc.) are correct
- Check you're using the right environment's BASE_URL
- Ensure the component/environment exists

### "HTTP 403 Forbidden"

- Check access token has necessary permissions
- Verify you have access to the organization/project
- Contact Choreo administrator for access

## Configuration Template

Save this as `.env.template` (do not commit actual values):

```bash
# Choreo Configuration Template
# Copy to .env and fill in actual values for local testing

BASE_URL=https://apis.choreo.dev/devops/1.0.0
ACCESS_TOKEN=your_access_token_here
ORG_UUID=your_org_uuid_here
PROJECT_ID=your_project_id_here
COMPONENT_ID=your_component_id_here
ENV_ID=your_env_id_here
APP_ENV_ID=your_app_env_id_here
```

## Next Steps

After configuration:

1. ✅ Test locally with `./scripts/test-sync.sh`
2. ✅ Commit a test change to `resources/` directory
3. ✅ Push to `resources` branch
4. ✅ Verify GitHub Action runs successfully
5. ✅ Check Choreo console for created ConfigMaps/mounts
6. ✅ Document any environment-specific notes

---

**Need Help?**

- Check workflow logs in GitHub Actions
- Review [README_FILE_MOUNTS.md](README_FILE_MOUNTS.md)
- Consult [FILE_MOUNT_API_REFERENCE.md](FILE_MOUNT_API_REFERENCE.md)
