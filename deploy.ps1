# Recharge Checker Automatic GitHub Pusher

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "       RECHARGE CHECKER GITHUB PUSHER" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Ask for the GitHub repository URL
$repoUrl = Read-Host "Apna GitHub Repository URL dalein (e.g., https://github.com/username/repo-name.git)"

if (-not $repoUrl) {
    Write-Host "Error: GitHub Repository URL zaroori hai!" -ForegroundColor Red
    Exit
}

# 1. Initialize Git if not already done
if (-not (Test-Path ".git")) {
    Write-Host "Git repository initialize kar rahe hain..." -ForegroundColor Yellow
    git init
}

# 2. Stage all files
Write-Host "Files stage (add) kar rahe hain..." -ForegroundColor Yellow
git add .

# 3. Commit files
Write-Host "Commit create kar rahe hain..." -ForegroundColor Yellow
git commit -m "Deploying to Render via Antigravity"

# 4. Set branch to main
git branch -M main

# 5. Link to Remote repository
Write-Host "GitHub remote origin check aur set kar rahe hain..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin $repoUrl

# 6. Push to GitHub
Write-Host "Code ko GitHub par push kar rahe hain (Isme aapka GitHub login/pass popup aa sakta hai)..." -ForegroundColor Yellow
git push -u origin main --force

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "SUCCESS: Aapka backend code GitHub par push ho gaya!" -ForegroundColor Green
Write-Host "Ab aap Render.com par jakar host kar sakte hain." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
