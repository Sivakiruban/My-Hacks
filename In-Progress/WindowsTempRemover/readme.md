# Windows Temp & Cache Cleaner (GUI & CLI)

A lightweight Python automation tool with a Tkinter interface to clean Windows temporary directories, prefetch data, and recent shortcuts. It mirrors the native Windows cleanup behavior by silently skipping files actively locked by running processes while reclaiming storage space.

> **Disclaimer:** This tool deletes cached files and temporary directories. Running with Administrator privileges allows the modification of system-level temp and prefetch folders. Review the script contents before execution. Provided "AS IS" without warranty.

---

## Targeted Directories

| Name | Path Cleaned | Description | Elevation Required |
|---|---|---|---|
| **Prefetch** | `C:\Windows\Prefetch` | Application execution traces & pre-cache data | Yes (Admin) |
| **System Temp** | `C:\Windows\Temp` | Temporary files created by background Windows services | Yes (Admin) |
| **User Temp (`%temp%`)** | `C:\Users\<user>\AppData\Local\Temp` | Temporary application caches and session scratchpads | No |
| **Recent** | `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent` | Shell history shortcuts (`.lnk`) while protecting system subfolders | No |

---

## Features

- **Dynamic Environment Resolution:** Automatically detects the logged-in user without hardcoding paths.
- **Fail-Safe File Operations:** Gracefully catches `PermissionError` and file locks (mirroring the Windows "Skip" dialog) instead of crashing.
- **Junction & System Protected:** Preserves Windows junction nodes and system-critical subdirectories (`AutomaticDestinations`, `CustomDestinations`).
- **Responsive Tkinter GUI:** Runs file-purging tasks on a background daemon thread with queue-based UI polling to eliminate interface freezing.
- **UAC Auto-Elevation:** Automatically prompts for administrative rights if run in user space.

---

## Prerequisites

- **Operating System:** Windows 10 / Windows 11
- **Python Version:** Python 3.9 or higher

---


**For building application from a Tkinter based python file:**
pip install pyinstaller

pyinstaller --onefile --windowed --uac-admin cleaner_gui.py

What These Flags Do:
--onefile: Packages Python, Tkinter, and your script into a single .exe file.

--windowed (or -w): Hides the black terminal/console window so only the Tkinter GUI opens.

--uac-admin: Embeds an application manifest that automatically triggers the Windows User Account Control (UAC) prompt on double-click, ensuring it runs as Administrator immediately without needing manual elevation code.

