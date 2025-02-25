#!/bin/bash

# Create secrets directory if it doesn't exist
SECRETS_DIR="./secrets"
mkdir -p "$SECRETS_DIR"
echo "Created secrets directory: $SECRETS_DIR"

# Function to create a secret file if it doesn't exist
create_secret_file() {
    local file_name="$1"
    local default_value="$2"
    local file_path="$SECRETS_DIR/$file_name"
    
    if [ ! -f "$file_path" ]; then
        echo -n "$default_value" > "$file_path"
        echo "Created secret file: $file_path with default value"
    else
        echo "Secret file already exists: $file_path"
    fi
}

# Create secret files with default values
create_secret_file "postgres_user.txt" "crawl4ai"
create_secret_file "postgres_password.txt" "change_this_password"
create_secret_file "postgres_db.txt" "crawl4ai"
create_secret_file "encryption_key.txt" "change_this_encryption_key"

echo ""
echo "Secret files have been created in the $SECRETS_DIR directory."
echo "IMPORTANT: Update the values in these files with your secure credentials before deploying to production."
echo "For development, you can use the .env file instead."
