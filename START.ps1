# Quick launch script for Proctoring AI
# Double-click this file or run: powershell -ExecutionPolicy Bypass -File .\START.ps1

$PYTHON_PATH = "D:/Computer Vision/Draft2/.proct-venv/Scripts/python.exe"
$PROJECT_DIR = "d:\Computer Vision\Draft2\Proctoring-AI"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "            PROCTORING AI - QUICK START" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose an option:" -ForegroundColor Green
Write-Host ""
Write-Host "  ⭐ 1. INTEGRATED DASHBOARD (ALL-IN-ONE) ⭐" -ForegroundColor Cyan
Write-Host "  ────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "  2. Eye Tracking" -ForegroundColor White
Write-Host "  3. Head Pose Detection" -ForegroundColor White
Write-Host "  4. Mouth Opening Detection" -ForegroundColor White
Write-Host "  5. Person & Phone Detection" -ForegroundColor White
Write-Host "  6. Face Spoofing Detection" -ForegroundColor White
Write-Host "  7. Start FastAPI Server" -ForegroundColor White
Write-Host "  8. Show Demo Menu" -ForegroundColor White
Write-Host "  9. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-9)"

Set-Location $PROJECT_DIR

switch ($choice) {
    "1" {
        Write-Host "`n🎯 Starting INTEGRATED DASHBOARD...`n" -ForegroundColor Cyan
        Write-Host "This combines ALL proctoring features in one interface!" -ForegroundColor Green
        Write-Host "Press 'q' to quit, 's' to save screenshot`n" -ForegroundColor Yellow
        & $PYTHON_PATH run_demo.py dashboard
    }
    "2" {
        Write-Host "`nStarting Eye Tracking... (Press 'q' to quit)`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py eye_tracking
    }
    "3" {
        Write-Host "`nStarting Head Pose Detection... (Press 'q' to quit)`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py head_pose
    }
    "4" {
        Write-Host "`nStarting Mouth Opening Detection... (Press 'r' to record, 'q' to quit)`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py mouth_opening
    }
    "5" {
        Write-Host "`nStarting Person & Phone Detection... (Press 'q' to quit)`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py person_phone
    }
    "6" {
        Write-Host "`nStarting Face Spoofing Detection... (Press 'q' to quit)`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py face_spoofing
    }
    "7" {
        Write-Host "`nStarting FastAPI Server...`n" -ForegroundColor Green
        Write-Host "API Documentation will be available at: http://localhost:8000/docs`n" -ForegroundColor Yellow
        & $PYTHON_PATH main.py
    }
    "8" {
        Write-Host "`nLaunching Demo Menu...`n" -ForegroundColor Green
        & $PYTHON_PATH run_demo.py
    }
    "9" {
        Write-Host "`nGoodbye!`n" -ForegroundColor Cyan
        exit
    }
    default {
        Write-Host "`nInvalid choice. Please run the script again.`n" -ForegroundColor Red
    }
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
