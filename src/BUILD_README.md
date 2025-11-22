# Building exe file for PyCalculator

## Quick Build

To quickly build an exe file, run the PowerShell script:

```powershell
.\build_exe.ps1
```

## Script Parameters

- **No parameters**: Full build with dependency installation
- **`-Clean`**: Clean previous builds before new build
- **`-NoInstall`**: Skip dependency installation (if already installed)

### Usage Examples:

```powershell
# Full build with cleanup
.\build_exe.ps1 -Clean

# Quick build without reinstalling dependencies
.\build_exe.ps1 -NoInstall

# Cleanup and full reinstallation
.\build_exe.ps1 -Clean
```

## What the script does

1. **Checks for Python** availability in the system
2. **Installs dependencies** from `requirements.txt`
3. **Checks and installs PyInstaller** (if needed)
4. **Runs build** of exe file using PyInstaller
5. **Checks result** and shows information about the created file

## Build Result

After successful build:
- `main.exe` file will appear in the `dist/` folder
- This is a ready-to-run application
- exe file can be copied and run on other computers without installing Python

## Requirements

- **Windows** with Python 3.7+ installed
- **PowerShell** (available by default in Windows)
- **Internet connection** for downloading dependencies (on first build)

## Troubleshooting

### Python not found
Make sure Python is installed and added to PATH:
1. Download Python from the official website
2. During installation, check "Add Python to PATH"
3. Restart PowerShell

### Access Error
Run PowerShell as administrator:
```powershell
# Right-click PowerShell and select "Run as administrator"
```

### Error installing dependencies
Check internet connection and pip access rights.

## Project Structure After Build

```
PyCalculator/
├── dist/              # Ready exe file
│   └── main.exe      # Application executable
├── build/            # Temporary build files
├── main.py           # Entry point
├── main.spec         # PyInstaller configuration
├── requirements.txt  # Dependencies
└── build_exe.ps1     # Build script
```
