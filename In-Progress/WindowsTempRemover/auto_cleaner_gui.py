import os
import sys
import stat
import shutil
import ctypes
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

def is_admin() -> bool:
    """Check if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return False

def elevate_if_needed():
    """Prompt to re-launch the script with elevated UAC permissions if not admin."""
    if not is_admin():
        result = messagebox.askyesno(
            "Administrator Access Recommended",
            "Folders like 'Prefetch' and 'System Temp' require administrator rights to clean.\n\n"
            "Would you like to restart the application as Administrator?"
        )
        if result:
            # Re-launch current script with runas verb
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(f'"{arg}"' for arg in sys.argv), None, 1
            )
            sys.exit(0)

def handle_remove_readonly(func, path, exc_info):
    """Clear read-only attribute if deletion fails due to file attributes."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def get_target_directories() -> dict[str, Path]:
    windir = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    user_profile = Path.home()

    return {
        "Prefetch": windir / "Prefetch",
        "User Temp (%temp%)": local_app_data / "Temp",
        "System Temp (temp)": windir / "Temp",
        "Recent": user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"
    }

class CleanerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows Temporary File Cleaner")
        self.geometry("780x560")
        self.minsize(680, 480)

        self.msg_queue = queue.Queue()
        self.is_running = False

        self._build_ui()
        self._check_queue()

    def _build_ui(self):
        # Header Frame
        header = ttk.Frame(self, padding=12)
        header.pack(fill=tk.X)

        user_str = os.environ.get("USERNAME", "Unknown")
        admin_status = "Elevated (Admin)" if is_admin() else "Standard User (Non-Admin)"
        admin_color = "#008000" if is_admin() else "#B22222"

        ttk.Label(header, text=f"Logged in User: {user_str}", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W)
        status_lbl = tk.Label(header, text=f"Privilege Status: {admin_status}", fg=admin_color, font=("Segoe UI", 9))
        status_lbl.pack(anchor=tk.W)

        # Progress Frame
        prog_frame = ttk.Frame(self, padding=(12, 0))
        prog_frame.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(prog_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))

        self.status_var = tk.StringVar(value="Ready. Click 'Start Cleanup' to begin.")
        ttk.Label(prog_frame, textvariable=self.status_var, font=("Segoe UI", 9)).pack(anchor=tk.W)

        # Summary Treeview Table
        table_frame = ttk.LabelFrame(self, text="Summary Table", padding=8)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        columns = ("folder", "path", "deleted", "skipped", "freed")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("folder", text="Folder Name")
        self.tree.heading("path", text="Resolved Path")
        self.tree.heading("deleted", text="Deleted Items")
        self.tree.heading("skipped", text="Skipped (Locked)")
        self.tree.heading("freed", text="Freed Space")

        self.tree.column("folder", width=140, anchor=tk.W)
        self.tree.column("path", width=280, anchor=tk.W)
        self.tree.column("deleted", width=90, anchor=tk.CENTER)
        self.tree.column("skipped", width=100, anchor=tk.CENTER)
        self.tree.column("freed", width=90, anchor=tk.E)

        # Scrollbar for table
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Pre-populate table with initial folders
        targets = get_target_directories()
        for name, path in targets.items():
            self.tree.insert("", tk.END, iid=name, values=(name, str(path), "0", "0", "0.00 MB"))

        # Footer Frame
        footer = ttk.Frame(self, padding=12)
        footer.pack(fill=tk.X)

        self.total_label = ttk.Label(footer, text="Total Space Freed: 0.00 MB", font=("Segoe UI", 10, "bold"))
        self.total_label.pack(side=tk.LEFT)

        self.btn_clean = ttk.Button(footer, text="Start Cleanup", command=self.start_cleanup)
        self.btn_clean.pack(side=tk.RIGHT)

    def start_cleanup(self):
        if self.is_running:
            return
        self.is_running = True
        self.btn_clean.configure(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.status_var.set("Scanning directories...")

        # Run background thread
        threading.Thread(target=self._worker_cleanup, daemon=True).start()

    def _worker_cleanup(self):
        targets = get_target_directories()
        
        # Count total items across all locations for progress tracking
        all_items = []
        for name, path in targets.items():
            if path.exists():
                try:
                    for item in path.iterdir():
                        all_items.append((name, item))
                except (PermissionError, OSError):
                    pass

        total_items_count = len(all_items)
        self.msg_queue.put(("set_progress_max", total_items_count if total_items_count > 0 else 1))

        folder_stats = {name: {"deleted": 0, "skipped": 0, "bytes": 0} for name in targets}
        total_freed_bytes = 0
        processed_count = 0

        for folder_name, item in all_items:
            processed_count += 1
            item_size = 0
            
            try:
                if item.is_file() or item.is_symlink():
                    item_size = item.stat().st_size
                elif item.is_dir():
                    item_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
            except (PermissionError, OSError):
                item_size = 0

            # Attempt deletion
            deleted = False
            try:
                if item.is_file() or item.is_symlink():
                    try:
                        item.unlink()
                        deleted = True
                    except PermissionError:
                        os.chmod(item, stat.S_IWRITE)
                        item.unlink()
                        deleted = True
                elif item.is_dir():
                    shutil.rmtree(item, onerror=handle_remove_readonly)
                    deleted = True
            except (PermissionError, OSError):
                # File locked or access restricted (equivalent to Windows "Skip")
                deleted = False

            if deleted:
                folder_stats[folder_name]["deleted"] += 1
                folder_stats[folder_name]["bytes"] += item_size
                total_freed_bytes += item_size
            else:
                folder_stats[folder_name]["skipped"] += 1

            # Dispatch incremental updates every 15 items to optimize GUI performance
            if processed_count % 15 == 0 or processed_count == total_items_count:
                self.msg_queue.put(("progress_update", processed_count, folder_name, folder_stats[folder_name], total_freed_bytes))

        self.msg_queue.put(("completed", folder_stats, total_freed_bytes))

    def _check_queue(self):
        """Poll the thread-safe queue and apply changes to Tkinter elements."""
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                mtype = msg[0]

                if mtype == "set_progress_max":
                    self.progress_bar["maximum"] = msg[1]
                elif mtype == "progress_update":
                    count, fname, stats, total_bytes = msg[1], msg[2], msg[3], msg[4]
                    self.progress_bar["value"] = count
                    self.status_var.set(f"Cleaning: {fname} ({count} items processed)")
                    mb = stats["bytes"] / (1024 * 1024)
                    
                    targets = get_target_directories()
                    self.tree.item(fname, values=(fname, str(targets[fname]), stats["deleted"], stats["skipped"], f"{mb:.2f} MB"))
                    self.total_label.configure(text=f"Total Space Freed: {total_bytes / (1024 * 1024):.2f} MB")
                elif mtype == "completed":
                    folder_stats, total_bytes = msg[1], msg[2]
                    targets = get_target_directories()
                    for fname, stats in folder_stats.items():
                        mb = stats["bytes"] / (1024 * 1024)
                        self.tree.item(fname, values=(fname, str(targets[fname]), stats["deleted"], stats["skipped"], f"{mb:.2f} MB"))
                    
                    total_mb = total_bytes / (1024 * 1024)
                    self.total_label.configure(text=f"Total Space Freed: {total_mb:.2f} MB")
                    self.status_var.set("Cleanup completed successfully.")
                    self.progress_bar["value"] = self.progress_bar["maximum"]
                    self.btn_clean.configure(state=tk.NORMAL)
                    self.is_running = False
                    messagebox.showinfo("Done", f"Cleanup finished!\nFreed a total of {total_mb:.2f} MB.")
        except queue.Empty:
            pass

        self.after(50, self._check_queue)

if __name__ == "__main__":
    elevate_if_needed()
    app = CleanerApp()
    app.mainloop()