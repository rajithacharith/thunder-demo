#!/bin/bash
# Local test script for file mount synchronization
# This script helps you test the sync process locally before pushing to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Thunder File Mount Sync - Local Test${NC}"
echo "=============================================="
echo ""

# Check if required environment variables are set
check_env_var() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}❌ Error: $1 is not set${NC}"
        return 1
    else
        echo -e "${GREEN}✓${NC} $1 is set"
        return 0
    fi
}

echo "Checking environment variables..."
MISSING_VARS=0

check_env_var "BASE_URL" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "ACCESS_TOKEN" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "ORG_UUID" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "PROJECT_ID" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "COMPONENT_ID" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "ENV_ID" || MISSING_VARS=$((MISSING_VARS + 1))
check_env_var "APP_ENV_ID" || MISSING_VARS=$((MISSING_VARS + 1))

echo ""

if [ $MISSING_VARS -gt 0 ]; then
    echo -e "${RED}❌ $MISSING_VARS required environment variable(s) missing${NC}"
    echo ""
    echo "Please set the required variables:"
    echo ""
    echo "  export BASE_URL='https://apis.choreo.dev/devops/1.0.0'"
    echo "  export ACCESS_TOKEN='your_access_token'"
    echo "  export ORG_UUID='your_org_uuid'"
    echo "  export PROJECT_ID='your_project_id'"
    echo "  export COMPONENT_ID='your_component_id'"
    echo "  export ENV_ID='your_env_id'"
    echo "  export APP_ENV_ID='your_app_env_id'"
    echo ""
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 is installed"
echo ""

# Check if requests library is installed
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠ 'requests' library not found. Installing...${NC}"
    pip3 install -r scripts/requirements.txt
fi

echo -e "${GREEN}✓${NC} Python dependencies are installed"
echo ""

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} In git repository"
echo ""

# Ask for confirmation
echo -e "${YELLOW}⚠ This will sync your local changes to Choreo${NC}"
echo ""
echo "Environment: ${BASE_URL}"
echo "Component: ${COMPONENT_ID}"
echo ""
read -p "Do you want to proceed? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "=============================================="
echo -e "${GREEN}🚀 Starting synchronization...${NC}"
echo "=============================================="
echo ""

# Set GITHUB_WORKSPACE if not set (for local testing)
export GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-$(pwd)}

# Run the sync script
python3 scripts/sync_file_mounts.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=============================================="
    echo -e "${GREEN}✅ Synchronization completed successfully!${NC}"
    echo "=============================================="
else
    echo ""
    echo "=============================================="
    echo -e "${RED}❌ Synchronization failed!${NC}"
    echo "=============================================="
    exit 1
fi
