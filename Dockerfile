# ----------------------------------------------------------------------------
# Copyright (c) 2025, WSO2 LLC. (https://www.wso2.com).
#
# WSO2 LLC. licenses this file to you under the Apache License,
# Version 2.0 (the "License"); you may not use this file except
# in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
# ----------------------------------------------------------------------------

# WSO2 Thunder Docker Image for Choreo Deployment
# This Dockerfile creates an optimized image for deploying Thunder on Choreo platform
# It uses the existing Thunder Docker image as a base and adds Choreo-specific configurations

# Use the existing Thunder image as base
# You can specify the version tag as needed (e.g., v0.15.0, latest)
ARG THUNDER_VERSION=latest
FROM ghcr.io/asgardeo/thunder:${THUNDER_VERSION}

# Switch to root for configuration changes
USER root

# Install additional utilities if needed for Choreo
RUN apk add --no-cache \
    jq \
    yq

# Create directory for Choreo-specific configurations
RUN mkdir -p /opt/thunder/choreo-config

# Copy deployment configuration
COPY deployment.yaml /opt/thunder/repository/conf/deployment.yaml

# Environment variables for Choreo deployment
# These can be overridden at runtime via Helm chart or Choreo platform
ENV SERVER_HOST="0.0.0.0" \
    SERVER_PORT="8090" \
    LOG_LEVEL="INFO" \
    DATABASE_TYPE="sqlite"

# Create a startup script for Choreo that handles dynamic configuration
RUN cat > /opt/thunder/choreo-start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Thunder on Choreo Platform..."

# Update deployment.yaml with environment variables if provided
DEPLOYMENT_CONFIG="/opt/thunder/repository/conf/deployment.yaml"

# Ensure database directories exist for SQLite
if [ "$DATABASE_TYPE" = "sqlite" ]; then
    mkdir -p /opt/thunder/repository/database
    echo "📁 SQLite database directory ready"
fi

# Update server hostname if provided
if [ -n "$SERVER_HOST" ] && [ -f "$DEPLOYMENT_CONFIG" ]; then
    echo "📝 Updating server hostname to: $SERVER_HOST"
    sed -i "s/hostname: \".*\"/hostname: \"${SERVER_HOST}\"/" "$DEPLOYMENT_CONFIG"
fi

# Update server port if provided
if [ -n "$SERVER_PORT" ] && [ -f "$DEPLOYMENT_CONFIG" ]; then
    echo "📝 Updating server port to: $SERVER_PORT"
    sed -i "s/port: [0-9]*/port: ${SERVER_PORT}/" "$DEPLOYMENT_CONFIG"
fi

# Update CORS allowed origins if provided
if [ -n "$CORS_ALLOWED_ORIGINS" ] && [ -f "$DEPLOYMENT_CONFIG" ]; then
    echo "📝 Updating CORS allowed origins"
    # This is a simplified update - you may need more sophisticated YAML editing
    # for complex CORS configurations
fi

# Update public URL if provided
if [ -n "$PUBLIC_URL" ]; then
    echo "📝 Setting public URL to: $PUBLIC_URL"
    if grep -q "public_url:" "$DEPLOYMENT_CONFIG"; then
        sed -i "s|public_url: \".*\"|public_url: \"${PUBLIC_URL}\"|" "$DEPLOYMENT_CONFIG"
    else
        sed -i "/hostname: \"${SERVER_HOST}\"/a\  public_url: \"${PUBLIC_URL}\"" "$DEPLOYMENT_CONFIG"
    fi
fi

# Log configuration status
echo "🔧 Configuration applied:"
echo "   - Server Host: ${SERVER_HOST}"
echo "   - Server Port: ${SERVER_PORT}"
echo "   - Database Type: ${DATABASE_TYPE}"
echo "   - Public URL: ${PUBLIC_URL:-<using config file>}"

# Start Thunder server
echo "⚡ Starting Thunder server..."
exec ./start.sh
EOF

# Make the startup script executable
RUN chmod +x /opt/thunder/choreo-start.sh

# Health check for Choreo platform
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -k -f https://localhost:${SERVER_PORT}/health || exit 1

# Switch back to thunder user for security
RUN chown -R thunder:thunder /opt/thunder
USER thunder

# Expose the server port
EXPOSE 8090

# Use the Choreo startup script
CMD ["/opt/thunder/choreo-start.sh"]
