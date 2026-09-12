@echo off
setlocal

:: Set variables
set URL=https://videos.geeksforgeeks.org/live_zoom_projects-in-21-days-batch-x-class2/1/video.m3u8
set REFERER=https://www.geeksforgeeks.org/
set UA=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36
set RAW=0day4.mp4
set CLEAN=gfg_day4.mp4
REM In cases of cookies not present in headers, we use --cookies "cookies.txt" by downloading them via browser extension.
REM Or we can use the Referrer header and User-Agent header to mimic browser requests.

:: Download with yt-dlp
yt-dlp --add-header "Referer: %REFERER%" ^
       --add-header "User-Agent: %UA%" ^
       -o "%RAW%" ^
       "%URL%"
echo ____Download_completed____
echo yt-dlp download completed. Raw file: %RAW%

:: Remux with ffmpeg
ffmpeg -i "%RAW%" -c copy "%CLEAN%"
echo ____Remuxing_completed____
echo FFmpeg remux completed. Final file: %CLEAN%
:: timeout /t 5 >nul
pause

endlocal
:: End of script