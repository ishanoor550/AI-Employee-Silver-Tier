@echo off
chcp 65001 >nul
echo ========================================
echo   AI Employee Silver Tier - Setup
echo ========================================
echo.

echo [1/4] Installing Python dependencies...
pip install playwright google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
if %errorlevel% neq 0 (
    echo WARNING: Some packages failed to install. Trying individual installs...
    pip install python-dotenv
)

echo [2/4] Installing Playwright browser (Chromium)...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo NOTE: Playwright browser install failed. 
    echo Run manually later: playwright install chromium
)

echo [3/4] Creating Windows Scheduled Task...
python src\scheduler.py --create-task

echo [4/4] Setting up environment file...
if not exist .env (
    echo # AI Employee Environment Configuration > .env
    echo # Uncomment and fill in your credentials >> .env
    echo. >> .env
    echo # Gmail API Credentials >> .env
    echo # GMAIL_CLIENT_ID=your_client_id >> .env
    echo # GMAIL_CLIENT_SECRET=your_client_secret >> .env
    echo. >> .env
    echo # SMTP Email Settings >> .env
    echo # SMTP_SERVER=smtp.gmail.com >> .env
    echo # SMTP_PORT=587 >> .env
    echo # SMTP_USER=your_email@gmail.com >> .env
    echo # SMTP_PASS=your_app_password >> .env
    echo # DRY_RUN=true >> .env
    echo. >> .env
    echo # LinkedIn Credentials >> .env
    echo # LINKEDIN_EMAIL=your_email >> .env
    echo # LINKEDIN_PASSWORD=your_password >> .env
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env with your credentials
echo   2. Run: .\run_silver.ps1
echo   3. Or run directly: python src\orchestrator.py
echo.
pause
