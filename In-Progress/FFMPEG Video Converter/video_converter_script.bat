@echo off
setlocal EnableDelayedExpansion
title FFmpeg Video Compressor

echo ================================
echo   FFmpeg Video Compressor
echo ================================
echo.

:: -----------------------------
:: Input file
:: -----------------------------
if "%~1"=="" (
    set /p INPUT=Enter input video filename: 
) else (
    set INPUT=%~1
)

if not exist "%INPUT%" (
    echo.
    echo ERROR: File not found!
    pause
    exit /b
)

:: -----------------------------
:: Choose codec
:: -----------------------------
echo.
echo Choose video codec:
echo   1 - x264 (H.264) [faster, larger file]
echo   2 - x265 (H.265) [slower, smaller file]
set /p CODEC_CHOICE=Enter choice (1 or 2): 

if "%CODEC_CHOICE%"=="2" (
    set VCODEC=libx265
) else (
    set VCODEC=libx264
)

:: -----------------------------
:: CRF
:: -----------------------------
echo.
echo Enter CRF value (recommended):
echo   18 = Very high quality
echo   20 = High quality
echo   23 = Balanced (default)
echo   26 = Smaller file
set /p CRF=CRF value [23]: 
if "%CRF%"=="" set CRF=23

:: -----------------------------
:: Preset
:: -----------------------------
echo.
echo Choose preset:
echo   ultrafast, superfast, veryfast, faster, fast
echo   medium (default)
echo   slow, slower, veryslow
set /p PRESET=Preset [medium]: 
if "%PRESET%"=="" set PRESET=medium

:: -----------------------------
:: Audio options
:: -----------------------------
echo.
echo Audio options:
echo   1 - Copy audio (no change, best quality)
echo   2 - AAC encode
set /p AUDIO_CHOICE=Enter choice (1 or 2): 

if "%AUDIO_CHOICE%"=="2" (
    set ACODEC=aac
    echo.
    echo Enter AAC bitrate (kbps):
    echo   96  = Small
    echo   128 = Good
    echo   160 = Very good
    echo   192 = Transparent
    set /p ABR=Bitrate [128]: 
    if "%ABR%"=="" set ABR=128
    set AUDIO_OPTS=-c:a aac -b:a %ABR%k
) else (
    set AUDIO_OPTS=-c:a copy
)

:: -----------------------------
:: Output filename
:: -----------------------------
set OUTFILE=%~nINPUT%_%VCODEC%_crf%CRF%_%PRESET%.mp4

:: -----------------------------
:: Run FFmpeg
:: -----------------------------
echo.
echo ================================
echo Encoding...
echo Codec: %VCODEC%
echo CRF: %CRF%
echo Preset: %PRESET%
echo Audio: %AUDIO_OPTS%
echo ================================
echo.

ffmpeg -i "%INPUT%" -c:v %VCODEC% -crf %CRF% -preset %PRESET% %AUDIO_OPTS% "%OUTFILE%"

echo.
echo Done!
echo Output file: %OUTFILE%
pause
