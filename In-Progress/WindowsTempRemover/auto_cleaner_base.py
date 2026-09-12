import os
import shutil
import stat
from pathlib import Path

def get_target_directories() -> dict[str, Path]:
    """Resolves standard Windows paths dynamically using environment variables."""
    windir = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    user_profile = Path.home()

    return {
        "Prefetch": windir / "Prefetch",
        "User Temp (%temp%)": local_app_data / "Temp",
        "System Temp (temp)": windir / "Temp",
        "Recent": user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"
    }

def handle_remove_readonly(func, path, exc_info):
    """Clears read-only attributes if deletion fails due to file permissions."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def clean_directory(dir_path: Path) -> dict:
    stats = {"deleted": 0, "skipped": 0, "bytes_freed": 0}

    if not dir_path.exists():
        return stats

    # Iterate over every item directly inside the target directory
    for item in dir_path.iterdir():
        # Get file size before deletion for reporting
        item_size = 0
        try:
            if item.is_file() or item.is_symlink():
                item_size = item.stat().st_size
            elif item.is_dir():
                item_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
        except (PermissionError, OSError):
            item_size = 0

        # Attempt deletion
        try:
            # Toggle
            #"""
            if item.is_file() or item.is_symlink():
                try:
                    item.unlink()
                except PermissionError:
                    # Retry once after clearing read-only flag
                    os.chmod(item, stat.S_IWRITE)
                    item.unlink()
            elif item.is_dir():
                shutil.rmtree(item, onerror=handle_remove_readonly)
            #"""
            
            stats["deleted"] += 1
            stats["bytes_freed"] += item_size
            pass # Toggle: Comment out actual deletion for safety during testing

        except (PermissionError, OSError):
            # Matches Windows "Skip": file in use, locked, or protected
            stats["skipped"] += 1

    return stats

def run_cleaner():
    targets = get_target_directories()
    summary_data = []

    print(f"Current User: {os.environ.get('USERNAME')}")
    print("Starting cleanup...\n")

    # """ # For testing purposes, comment out the actual deletion and just print what would be cleaned
    for name, path in targets.items():
        print(f"Cleaning {name} at {path}...")
    #"""

    for name, path in targets.items():
        res = clean_directory(path)
        mb_freed = res["bytes_freed"] / (1024 * 1024)
        summary_data.append({
            "Folder": name,
            "Path": str(path),
            "Deleted": res["deleted"],
            "Skipped": res["skipped"],
            "Space Freed (MB)": f"{mb_freed:.2f} MB"
        })

    return summary_data

if __name__ == "__main__":
    results = run_cleaner()
    print("\nCleanup Summary:")
    for item in results:
        print(f" - {item['Folder']}: {item['Space Freed (MB)']}")