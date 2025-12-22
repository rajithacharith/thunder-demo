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

# Add thunder user with UID 10001 if not already present
RUN adduser -u 10001 -D thunder
# Switch back to thunder user for security
RUN chown -R thunder:thunder /opt/thunder
USER thunder

# Expose the server port
EXPOSE 8090

# Use the Choreo startup script
CMD ["/opt/thunder/start.sh"]
