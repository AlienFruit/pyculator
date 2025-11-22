# Script for building PyCalculator application exe file
# Run: .\build_exe.ps1

param(
    [switch]$Clean,
    [switch]$NoInstall
)

Write-Host "=== Building exe file for PyCalculator ===" -ForegroundColor Green

# Check for Python availability
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Install Python and add it to PATH." -ForegroundColor Red
    exit 1
}

# Clean previous builds (if -Clean parameter is specified)
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item "build" -Recurse -Force
        Write-Host "build folder removed" -ForegroundColor Green
    }
    if (Test-Path "dist") {
        Remove-Item "dist" -Recurse -Force
        Write-Host "dist folder removed" -ForegroundColor Green
    }
}

# Install dependencies (if -NoInstall parameter is not specified)
if (-not $NoInstall) {
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Error installing dependencies: $_" -ForegroundColor Red
        exit 1
    }

    # Install PyInstaller if not installed
    Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
    try {
        pyinstaller --version > $null 2>&1
        Write-Host "PyInstaller found" -ForegroundColor Green
    } catch {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        try {
            pip install pyinstaller
            Write-Host "PyInstaller installed" -ForegroundColor Green
        } catch {
            Write-Host "Error installing PyInstaller: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# Build exe file
Write-Host "Starting exe file build..." -ForegroundColor Yellow
try {
    pyinstaller main.spec --clean
    Write-Host "Build completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Build error: $_" -ForegroundColor Red
    exit 1
}

# Check result
$exePath = "dist\PyCalculator.exe"
if (Test-Path $exePath) {
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "Exe file created: $exePath (size: $([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green

    # Build information
    Write-Host "`n=== Build Information ===" -ForegroundColor Cyan
    Write-Host "Exe location: $exePath" -ForegroundColor White
    Write-Host "To run: .\dist\PyCalculator.exe" -ForegroundColor White
    Write-Host "dist folder contains the ready application" -ForegroundColor White
} else {
    Write-Host "Error: exe file not found after build" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Build completed ===" -ForegroundColor Green
