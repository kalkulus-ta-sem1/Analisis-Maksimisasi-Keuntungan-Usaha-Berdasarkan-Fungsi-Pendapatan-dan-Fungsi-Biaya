@echo off
title Aplikasi Kalkulus Optimasi UMKM Ketoprak
echo ============================================================
echo   PROYEK AKHIR KALKULUS DASAR - UNIVERSITAS SILIWANGI
echo   Penerapan Konsep Turunan dalam Optimasi Keuntungan UMKM
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    echo Menggunakan virtual environment lokal ^(.venv^)...
    ".venv\Scripts\python.exe" app.py
) else (
    echo Memeriksa instalasi Python...
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python belum terpasang atau belum masuk ke PATH!
        echo Silakan install Python 3.10+ dari python.org dan centang "Add Python to PATH".
        pause
        exit /b
    )

    echo Memeriksa dan menginstal dependensi ^(jika diperlukan^)...
    pip install -r requirements.txt >nul 2>&1

    echo.
    echo Menjalankan Aplikasi GUI Kalkulus UMKM...
    python app.py
)

if %errorlevel% neq 0 (
    echo.
    echo Terjadi kendala saat menjalankan aplikasi.
    pause
)
