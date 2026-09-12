"""
powercfg /batteryreport
"""
import subprocess
import os
import webbrowser

def generate_battery_report():
    # Run the powercfg command
    try:
        subprocess.run(["powercfg", "/batteryreport"], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to generate battery report:", e)
        return

    # Default output location
    report_path = os.path.expanduser("~\\battery-report.html")

    # Check if the report exists
    if os.path.exists(report_path):
        print(f"Battery report generated at: {report_path}")
        #webbrowser.open(report_path)
    else:
        print("Battery report not found. Check permissions or try running as administrator.")

generate_battery_report()