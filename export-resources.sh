#!/bin/bash

# Get IDs from environment variables
NOTIFICATION_SENDER_ID="${NOTIFICATION_SENDER_ID:-}"
FLOW_ID="${FLOW_ID:-}"
ASSERTION="${ASSERTION:-}"

# Create output directories if they don't exist
mkdir -p resources/notification_senders
mkdir -p resources/flows    

echo "📦 Exporting resources..."
echo ""

# Export notification sender
if [ -n "$NOTIFICATION_SENDER_ID" ]; then
    echo "🔹 Exporting notification sender with ID: $NOTIFICATION_SENDER_ID"
    RESPONSE=$(curl --location 'https://localhost:8090/export' -k \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/yaml' \
    --header "Authorization: Bearer ${ASSERTION}" \
    --silent \
    --data "{
        \"notificationSenders\": [
            \"$NOTIFICATION_SENDER_ID\"
        ],
        \"options\": {
            \"include_metadata\": true,
            \"format\": \"yaml\",
            \"folder_structure\": {
                \"group_by_type\": true,
                \"file_naming_pattern\": \"\${name}_\${id}\"
            }
        }
    }")

    if [ $? -eq 0 ] && [ -n "$RESPONSE" ]; then
        FILENAME=$(echo "$RESPONSE" | grep "# File:" | head -1 | sed 's/# File: //')
        
        if [ -z "$FILENAME" ]; then
            FILENAME="notification_sender_${NOTIFICATION_SENDER_ID}.yaml"
        fi
        
        OUTPUT_FILE="resources/notification_senders/$FILENAME"
        echo "$RESPONSE" > "$OUTPUT_FILE"
        
        echo "✅ Notification sender exported successfully to: $OUTPUT_FILE"
    else
        echo "❌ Failed to export notification sender"
    fi
else
    echo "⚠️  Skipping notification sender export (NOTIFICATION_SENDER_ID not set)"
    echo "💡 Set NOTIFICATION_SENDER_ID environment variable to export a notification sender"
fi

echo ""

# Export flow
if [ -n "$FLOW_ID" ]; then
    echo "🔹 Exporting flow with ID: $FLOW_ID"
    RESPONSE=$(curl --location 'https://localhost:8090/export' -k \
    --header 'Content-Type: application/json' \
    --header 'Accept: application/yaml' \
    --header "Authorization: Bearer ${ASSERTION}" \
    --silent \
    --data "{
        \"flows\": [
            \"$FLOW_ID\"
        ],
        \"options\": {
            \"include_metadata\": true,
            \"format\": \"yaml\",
            \"folder_structure\": {
                \"group_by_type\": true,
                \"file_naming_pattern\": \"\${name}_\${id}\"
            }
        }
    }")

    if [ $? -eq 0 ] && [ -n "$RESPONSE" ]; then
        FILENAME=$(echo "$RESPONSE" | grep "# File:" | head -1 | sed 's/# File: //')
        
        if [ -z "$FILENAME" ]; then
            FILENAME="flow_${FLOW_ID}.yaml"
        fi
        
        OUTPUT_FILE="resources/flows/$FILENAME"
        echo "$RESPONSE" > "$OUTPUT_FILE"
        
        echo "✅ Flow exported successfully to: $OUTPUT_FILE"
    else
        echo "❌ Failed to export flow"
    fi
else
    echo "⚠️  Skipping flow export (FLOW_ID not set)"
    echo "💡 Set FLOW_ID environment variable to export a flow"
fi

echo ""
echo "🎉 Export process completed!"
