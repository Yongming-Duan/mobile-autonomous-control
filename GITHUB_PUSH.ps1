# GitHub Repository Push Script
# 手机自主化控制系统 - GitHub 推送脚本

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  GitHub Repository Push Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set repository path
$REPO_PATH = "D:\工作日常\服务器搭建\荣耀手机刷机"

Write-Host "[Step 1/5] Checking repository status..." -ForegroundColor Yellow
Set-Location $REPO_PATH

# Check current branch
$CURRENT_BRANCH = git rev-parse --abbrev-ref HEAD
Write-Host "Current branch: $CURRENT_BRANCH" -ForegroundColor Green

# Check for uncommitted changes
$STATUS = git status --porcelain
if ($STATUS) {
    Write-Host "Warning: You have uncommitted changes:" -ForegroundColor Yellow
    Write-Host $STATUS
    $CONTINUE = Read-Host "Continue anyway? (y/n)"
    if ($CONTINUE -ne "y") {
        exit
    }
}
Write-Host ""

Write-Host "[Step 2/5] GitHub Repository Information" -ForegroundColor Yellow
Write-Host "Please provide your GitHub information:" -ForegroundColor Cyan
Write-Host ""

$GITHUB_USERNAME = Read-Host "GitHub username"
$REPO_NAME = Read-Host "Repository name (default: mobile-autonomous-control)"

if (-not $REPO_NAME) {
    $REPO_NAME = "mobile-autonomous-control"
}

Write-Host ""
Write-Host "Repository will be created at:" -ForegroundColor Green
Write-Host "https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host ""

$CONFIRM = Read-Host "Continue? (y/n)"
if ($CONFIRM -ne "y") {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}
Write-Host ""

Write-Host "[Step 3/5] Creating GitHub Repository..." -ForegroundColor Yellow
Write-Host "Please create the repository manually:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Visit: https://github.com/new" -ForegroundColor White
Write-Host "2. Repository name: $REPO_NAME" -ForegroundColor White
Write-Host "3. Description: Mobile Autonomous Control System - Complete Android phone control with sensors, AI, and web dashboard" -ForegroundColor White
Write-Host "4. Choose Public or Private" -ForegroundColor White
Write-Host "5. DO NOT initialize with README, .gitignore, or LICENSE" -ForegroundColor Yellow
Write-Host "6. Click 'Create repository'" -ForegroundColor White
Write-Host ""

$READY = Read-Host "Press Enter when repository is created..."

Write-Host ""
Write-Host "[Step 4/5] Configuring remote repository..." -ForegroundColor Yellow

# Remove old origin if exists
git remote remove origin 2>$null

# Add new remote
$REMOTE_URL = "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
git remote add origin $REMOTE_URL

Write-Host "Remote added: $REMOTE_URL" -ForegroundColor Green
Write-Host ""

Write-Host "[Step 5/5] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "This may take a few minutes for large repositories..." -ForegroundColor Cyan
Write-Host ""

# Push master branch
Write-Host "Pushing master branch..." -ForegroundColor Cyan
git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "Master branch pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to push master branch. You may need to authenticate." -ForegroundColor Red
    Write-Host ""
    Write-Host "To authenticate, you can:" -ForegroundColor Yellow
    Write-Host "1. Use a Personal Access Token:" -ForegroundColor White
    Write-Host "   - Create token at: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host "   - Select 'repo' scope" -ForegroundColor Gray
    Write-Host "   - Use token as password when prompted" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Or use SSH:" -ForegroundColor White
    Write-Host "   - Generate SSH key: ssh-keygen -t ed25519 -C 'your_email@example.com'" -ForegroundColor Gray
    Write-Host "   - Add to GitHub: https://github.com/settings/keys" -ForegroundColor Gray
    Write-Host "   - Change remote URL to git@github.com:$GITHUB_USERNAME/$REPO_NAME.git" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

# Push feature branch
Write-Host ""
Write-Host "Pushing feature branch..." -ForegroundColor Cyan
git push -u origin feature/autonomous-control-system

if ($LASTEXITCODE -eq 0) {
    Write-Host "Feature branch pushed successfully!" -ForegroundColor Green
} else {
    Write-Host "Failed to push feature branch." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Repository pushed to GitHub" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your repository" -ForegroundColor White
Write-Host "2. Create a Pull Request:" -ForegroundColor White
Write-Host "   - Base: master" -ForegroundColor Gray
Write-Host "   - Compare: feature/autonomous-control-system" -ForegroundColor Gray
Write-Host "   - Title: feat: 手机自主化控制系统完整实现" -ForegroundColor Gray
Write-Host ""
Write-Host "Or create PR using GitHub CLI if installed:" -ForegroundColor White
Write-Host "gh pr create --base master --head feature/autonomous-control-system" -ForegroundColor Gray
Write-Host ""
