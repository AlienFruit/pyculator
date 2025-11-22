# Скрипт для сборки exe файла приложения PyCalculator
# Запуск: .\build_exe.ps1

param(
    [switch]$Clean,
    [switch]$NoInstall
)

Write-Host "=== Сборка exe файла для PyCalculator ===" -ForegroundColor Green

# Проверка наличия Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Найден Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Python не найден. Установите Python и добавьте его в PATH." -ForegroundColor Red
    exit 1
}

# Очистка предыдущих сборок (если указан параметр -Clean)
if ($Clean) {
    Write-Host "Очистка предыдущих сборок..." -ForegroundColor Yellow
    if (Test-Path "build") {
        Remove-Item "build" -Recurse -Force
        Write-Host "Папка build удалена" -ForegroundColor Green
    }
    if (Test-Path "dist") {
        Remove-Item "dist" -Recurse -Force
        Write-Host "Папка dist удалена" -ForegroundColor Green
    }
}

# Установка зависимостей (если не указан параметр -NoInstall)
if (-not $NoInstall) {
    Write-Host "Установка зависимостей из requirements.txt..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "Зависимости установлены успешно" -ForegroundColor Green
    } catch {
        Write-Host "Ошибка при установке зависимостей: $_" -ForegroundColor Red
        exit 1
    }

    # Установка PyInstaller, если не установлен
    Write-Host "Проверка PyInstaller..." -ForegroundColor Yellow
    try {
        pyinstaller --version > $null 2>&1
        Write-Host "PyInstaller найден" -ForegroundColor Green
    } catch {
        Write-Host "Установка PyInstaller..." -ForegroundColor Yellow
        try {
            pip install pyinstaller
            Write-Host "PyInstaller установлен" -ForegroundColor Green
        } catch {
            Write-Host "Ошибка при установке PyInstaller: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# Сборка exe файла
Write-Host "Запуск сборки exe файла..." -ForegroundColor Yellow
try {
    pyinstaller main.spec --clean
    Write-Host "Сборка завершена успешно!" -ForegroundColor Green
} catch {
    Write-Host "Ошибка при сборке: $_" -ForegroundColor Red
    exit 1
}

# Проверка результата
$exePath = "dist\PyCalculator.exe"
if (Test-Path $exePath) {
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-Host "Exe файл создан: $exePath (размер: $([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green

    # Информация о сборке
    Write-Host "`n=== Информация о сборке ===" -ForegroundColor Cyan
    Write-Host "Расположение exe: $exePath" -ForegroundColor White
    Write-Host "Для запуска: .\dist\PyCalculator.exe" -ForegroundColor White
    Write-Host "Папка dist содержит готовое приложение" -ForegroundColor White
} else {
    Write-Host "Ошибка: exe файл не найден после сборки" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Сборка завершена ===" -ForegroundColor Green
