# Create secrets directory if it doesn't exist
$secretsDir = ".\secrets"
if (-not (Test-Path $secretsDir)) {
    New-Item -Path $secretsDir -ItemType Directory
    Write-Host "Created secrets directory: $secretsDir"
}

# Function to create a secret file if it doesn't exist
function Create-SecretFile {
    param (
        [string]$fileName,
        [string]$defaultValue
    )
    
    $filePath = Join-Path $secretsDir $fileName
    if (-not (Test-Path $filePath)) {
        $defaultValue | Out-File -FilePath $filePath -NoNewline
        Write-Host "Created secret file: $filePath with default value"
    } else {
        Write-Host "Secret file already exists: $filePath"
    }
}

# Create secret files with default values
Create-SecretFile -fileName "postgres_user.txt" -defaultValue "crawl4ai"
Create-SecretFile -fileName "postgres_password.txt" -defaultValue "change_this_password"
Create-SecretFile -fileName "postgres_db.txt" -defaultValue "crawl4ai"
Create-SecretFile -fileName "encryption_key.txt" -defaultValue "change_this_encryption_key"

Write-Host ""
Write-Host "Secret files have been created in the $secretsDir directory."
Write-Host "IMPORTANT: Update the values in these files with your secure credentials before deploying to production."
Write-Host "For development, you can use the .env file instead."
