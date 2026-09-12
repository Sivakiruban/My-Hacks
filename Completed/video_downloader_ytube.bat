@echo off
setlocal

:: ==============================
:: Configuration
:: ==============================

set "URL=https://www.youtube.com/watch?v=MTZwSjiDg30"

set "RAW=0day1.mp4"
set "CLEAN=si_day1.mp4"

:: ==============================
:: Download with yt-dlp
:: ==============================

echo.
echo ==============================
echo       Starting Download
echo ==============================
echo.

yt-dlp ^
    -o "%RAW%" ^
    "%URL%"

if errorlevel 1 (
    echo.
    echo [ERROR] yt-dlp download failed!
    echo Raw file was not successfully downloaded.
    pause
    exit /b 1
)

echo.
echo ____Download_completed____
echo yt-dlp download completed.
echo Raw file: %RAW%

:: ==============================
:: Remux with FFmpeg
:: ==============================

echo.
echo ==============================
echo       Remuxing with FFmpeg
echo ==============================
echo.

ffmpeg -i "%RAW%" -c copy "%CLEAN%"

if errorlevel 1 (
    echo.
    echo [ERROR] FFmpeg remux failed!
    pause
    exit /b 1
)

echo.
echo ____Remuxing_completed____
echo FFmpeg remux completed.
echo Final file: %CLEAN%

echo.
echo ==============================
echo          ALL DONE
echo ==============================
echo.

pause
endlocal