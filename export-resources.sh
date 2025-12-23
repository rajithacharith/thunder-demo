#!/bin/bash

ASSERTION="${ASSERTION:-}"

# Create output directories if they don't exist
mkdir -p resources/notification_senders
mkdir -p resources/flows    

echo "📦 Exporting resources..."
echo ""

RESPONSE=$(curl --location 'https://localhost:8090/export' -k \
--header 'Content-Type: application/json' \
--header 'Accept: application/yaml' \
--header "Authorization: Bearer ${ASSERTION}" \
--silent \
--data "{
    \"flows\": [\"*\"],
    \"notification_senders\": [\"*\"],
    \"applications\": [\"*\"],
    \"organization_unit\": [\"*\"],
    \"user_schema\": [\"*\"],
    \"options\": {
        \"include_metadata\": true,
        \"format\": \"yaml\",
        \"folder_structure\": {
            \"group_by_type\": true,
            \"file_naming_pattern\": \"\${name}\"
        }
    }
}")

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
    echo "❌ Failed to export resources"
    exit 1
fi

# Store the complete response to a text file
echo "$RESPONSE" > exported_resources.txt
echo "💾 Saved complete response to: exported_resources.txt"
echo ""

echo "📄 Processing exported resources..."
echo ""

# Save response to a temp file for processing
TEMP_FILE=$(mktemp)
echo "$RESPONSE" > "$TEMP_FILE"

# Function to extract and save individual YAML files
extract_yaml_files() {
    local current_file=""
    local current_content=""
    local in_document=false
    local resource_type=""
    
    while IFS= read -r line; do
        # Detect file header comment
        if [[ "$line" =~ ^#\ File:\ (.+)$ ]]; then
            # Save previous file if exists
            if [ -n "$current_file" ] && [ -n "$current_content" ]; then
                save_resource_file "$resource_type" "$current_file" "$current_content"
            fi
            
            # Start new file
            current_file="${BASH_REMATCH[1]}"
            current_content="$line"$'\n'
            in_document=true
            resource_type=""  # Reset, will be determined from content
            
        elif [[ "$line" == "---" ]] && [ "$in_document" = true ]; then
            # Document separator - save current and reset
            if [ -n "$current_file" ] && [ -n "$current_content" ]; then
                # Determine type from content if not already set
                if [ -z "$resource_type" ]; then
                    resource_type=$(detect_resource_type "$current_content" "$current_file")
                fi
                save_resource_file "$resource_type" "$current_file" "$current_content"
            fi
            current_file=""
            current_content=""
            in_document=false
            resource_type=""
            
        elif [ "$in_document" = true ]; then
            current_content+="$line"$'\n'
            
            # Detect resource type from content on the fly
            if [ -z "$resource_type" ]; then
                if [[ "$line" =~ ^flowType:\ (AUTHENTICATION|REGISTRATION) ]]; then
                    resource_type="flows"
                elif [[ "$line" =~ ^auth_flow_graph_id: ]] || [[ "$line" =~ ^inbound_auth_config: ]]; then
                    resource_type="applications"
                elif [[ "$line" =~ ^federation_protocol: ]] || [[ "$line" =~ ^idp_type: ]]; then
                    resource_type="identity_providers"
                elif [[ "$line" =~ ^ou_type: ]] || [[ "$line" =~ ^parent_ou_id: ]]; then
                    resource_type="organization_unit"
                elif [[ "$line" =~ ^schema_type: ]] || [[ "$line" =~ ^schema_attributes: ]]; then
                    resource_type="user_schema"
                elif [[ "$line" =~ ^sender_type: ]] || [[ "$line" =~ ^notification_provider: ]]; then
                    resource_type="notification_senders"
                fi
            fi
        fi
    done < "$TEMP_FILE"
    
    # Save the last file
    if [ -n "$current_file" ] && [ -n "$current_content" ]; then
        if [ -z "$resource_type" ]; then
            resource_type=$(detect_resource_type "$current_content" "$current_file")
        fi
        save_resource_file "$resource_type" "$current_file" "$current_content"
    fi
}

# Function to detect resource type from content and filename
detect_resource_type() {
    local content="$1"
    local filename="$2"
    
    # Check content for type indicators
    if echo "$content" | grep -q "^flowType:"; then
        echo "flows"
    elif echo "$content" | grep -q "^auth_flow_graph_id:\|^inbound_auth_config:"; then
        echo "applications"
    elif echo "$content" | grep -q "^federation_protocol:\|^idp_type:"; then
        echo "identity_providers"
    elif echo "$content" | grep -q "^ou_type:\|^parent_ou_id:"; then
        echo "organization_units"
    elif echo "$content" | grep -q "^schema_type:\|^schema_attributes:"; then
        echo "user_schemas"
    elif echo "$content" | grep -q "^sender_type:\|^notification_provider:"; then
        echo "notification_senders"
    # Fallback to filename patterns
    elif [[ "$filename" =~ _Flow\.yaml$ ]] || [[ "$filename" =~ _flow\.yaml$ ]]; then
        echo "flows"
    elif [[ "$filename" =~ _Application\.yaml$ ]] || [[ "$filename" =~ _application\.yaml$ ]]; then
        echo "applications"
    elif [[ "$filename" =~ _IDP\.yaml$ ]] || [[ "$filename" =~ _idp\.yaml$ ]]; then
        echo "identity_providers"
    elif [[ "$filename" =~ _OU\.yaml$ ]] || [[ "$filename" =~ _ou\.yaml$ ]]; then
        echo "organization_units"
    elif [[ "$filename" =~ _Schema\.yaml$ ]] || [[ "$filename" =~ _schema\.yaml$ ]]; then
        echo "user_schemas"
    elif [[ "$filename" =~ _Sender\.yaml$ ]] || [[ "$filename" =~ _sender\.yaml$ ]]; then
        echo "notification_senders"
    else
        # Default based on simple filename (if no underscore pattern, likely an application)
        echo "applications"
    fi
}

# Function to save resource file to appropriate directory
save_resource_file() {
    local type="$1"
    local filename="$2"
    local content="$3"
    
    local output_dir="resources/$type"
    mkdir -p "$output_dir"
    
    local output_path="$output_dir/$filename"
    echo "$content" > "$output_path"
    
    echo "✅ Saved: $output_path"
}

# Extract and save all files
extract_yaml_files

# Clean up temp file
rm -f "$TEMP_FILE"

echo ""
echo "🎉 Export process completed!"
