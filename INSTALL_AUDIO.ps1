# Installation Script for Audio Detection Dependencies
# Run this script to install audio detection requirements

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Audio Detection Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Installing audio detection dependencies..." -ForegroundColor Yellow
Write-Host ""

# Try installing PyAudio with pip first
Write-Host "Attempting to install PyAudio..." -ForegroundColor Cyan
$pyaudioInstalled = $false

try {
    pip install PyAudio 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PyAudio installed successfully via pip" -ForegroundColor Green
        $pyaudioInstalled = $true
    }
} catch {
    Write-Host "⚠ Direct pip install failed" -ForegroundColor Yellow
}

# If pip failed, try pipwin (Windows-specific)
if (-not $pyaudioInstalled) {
    Write-Host ""
    Write-Host "Trying alternative method with pipwin..." -ForegroundColor Yellow
    
    try {
        pip install pipwin
        pipwin install pyaudio
        Write-Host "✓ PyAudio installed successfully via pipwin" -ForegroundColor Green
        $pyaudioInstalled = $true
    } catch {
        Write-Host "⚠ pipwin installation failed" -ForegroundColor Yellow
    }
}

# If still failed, provide manual instructions
if (-not $pyaudioInstalled) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  PyAudio Installation Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install PyAudio manually:" -ForegroundColor Yellow
    Write-Host "1. Download the appropriate .whl file from:" -ForegroundColor White
    Write-Host "   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Install with:" -ForegroundColor White
    Write-Host "   pip install PyAudio-0.2.14-cpXXX-cpXXX-win_amd64.whl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Then run this script again" -ForegroundColor White
    Write-Host ""
}

# Install SpeechRecognition
Write-Host ""
Write-Host "Installing SpeechRecognition..." -ForegroundColor Cyan
try {
    pip install SpeechRecognition
    Write-Host "✓ SpeechRecognition installed successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to install SpeechRecognition" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Audio Detection" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test the audio detector
Write-Host "Running audio detector test..." -ForegroundColor Yellow
Write-Host ""

python -c "
try:
    from audio_detector import AudioDetector, AUDIO_AVAILABLE
    if AUDIO_AVAILABLE:
        print('✓ Audio detection is available and ready!')
        print('✓ Microphone access will be tested when you start monitoring')
    else:
        print('✗ Audio detection is not available')
        print('  Please check the installation steps above')
except Exception as e:
    print(f'✗ Error testing audio detector: {e}')
"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the proctoring system with audio detection:" -ForegroundColor Yellow
Write-Host "  python flask_app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "The system will automatically:" -ForegroundColor White
Write-Host "  • Start video monitoring" -ForegroundColor Green
Write-Host "  • Start audio monitoring" -ForegroundColor Green
Write-Host "  • Enable screenshot detection" -ForegroundColor Green
Write-Host "  • Log all violations" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
