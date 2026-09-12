Script: video_downloader.bat

Script does two things:
* Downloads the video file using the *yt-dlp* package
* Repairs the raw file using *ffmpeg* and outputs cleaned file.

Inputs to be given: [These can be found under Dev Tools -> Network -> headers]
URL - Actual video URL, 
REFERER - Website link, 
UA - User Agent, 
RAW - Input File or Raw File, 
CLEAN - Output File or cleaned with proper encodings.

Quick Looks on Installation and usages - Behind the scenes:
For Downloading - Used packages:
* yt-dlp
* ffmpeg

Downloads:
https://github.com/yt-dlp/yt-dlp/tree/master
- Installation -> yt-dlp.exe
https://ffmpeg.org/download.html#build-windows
- https://www.gyan.dev/ffmpeg/builds/

Two Commands that rule out all of this: // Usages
step1: [Downloading video using yt-dlp package]
yt-dlp --add-header "Referer: https://www.geeksforgeeks.org/" --add-header "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36" "https://videos.geeksforgeeks.org/live_zoom_projects-in-21-days-batch-x-class2/1/video.m3u8"

step2: [Fixing the yt-dlp downloaded Video using ffmpeg package]
ffmpeg -i 0day1.mp4 -c copy gfg_day1.mp4


**Other useful commads for youtube video:**
URL=actual ytube video url on url bar (not from devtools)
yt-dlp -v "URL"