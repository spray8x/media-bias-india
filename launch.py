import subprocess
import sys
import os
import webbrowser
import time
import threading

def open_browser():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

# determine streamlit path
if os.name == "nt":
    streamlit = os.path.join("venv", "Scripts", "streamlit.exe")
else:
    streamlit = os.path.join("venv", "bin", "streamlit")

if not os.path.exists(streamlit):
    print("Venv not found. Run setup.py first.")
    input("Press Enter to exit...")
    sys.exit(1)

print("Starting Indian Media Bias Dashboard...")
print("Opening browser at http://localhost:8501")
print("Press Ctrl+C to stop.\n")

threading.Thread(target=open_browser, daemon=True).start()

subprocess.run([streamlit, "run", "app.py"])
