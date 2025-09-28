# ----------------------------
# Cleanup Repo Script for GitHub
# Removes node_modules and large files from history
# ----------------------------

# Step 0: Go to repo folder (update path if needed)
$repoPath = "E:\New folder\streamlit backup"
Set-Location $repoPath

Write-Host "✅ Working in repo: $repoPath"

# Step 1: Check Python filter-repo installation
Write-Host "Checking if git-filter-repo is installed..."
$filterRepoCheck = pip show git-filter-repo
if (!$filterRepoCheck) {
    Write-Host "git-filter-repo not found. Installing..."
    pip install git-filter-repo
} else {
    Write-Host "git-filter-repo already installed."
}

# Step 2: Backup repo (optional but recommended)
$backupPath = "E:\streamlit-backup-copy"
Write-Host "Creating backup at $backupPath ..."
if (!(Test-Path $backupPath)) {
    xcopy $repoPath $backupPath /E /I
    Write-Host "Backup completed."
} else {
    Write-Host "Backup folder already exists, skipping backup."
}

# Step 3: Add node_modules to .gitignore
if (!(Test-Path ".gitignore")) { New-Item .gitignore -ItemType File -Force }
Add-Content .gitignore "node_modules/"
Write-Host ".gitignore updated with node_modules/"

# Step 4: Remove node_modules from staging (if exists)
git rm -r --cached node_modules 2>$null
Write-Host "node_modules removed from staging."

# Step 5: Commit changes
git add .gitignore
git commit -m "Remove node_modules and add to .gitignore" 2>$null
Write-Host "Committed removal of node_modules."

# Step 6: Clean repo history with git-filter-repo
Write-Host "Cleaning repo history: removing node_modules and large files..."
git filter-repo --path node_modules/ --invert-paths
Write-Host "Repo history cleaned."

# Step 7: Force push cleaned repo
Write-Host "Force pushing cleaned repo to origin (feature branch)..."
git push origin feature --force

Write-Host "🎉 Repo cleanup done! node_modules removed from history and pushed."
Write-Host "Check GitHub: your feature branch should now accept the push."
