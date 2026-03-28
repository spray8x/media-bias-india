import subprocess
import sys
import os

print("Setting up Indian Media Bias Dashboard...")

# create venv
subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

# determine pip path
pip = "venv/Scripts/pip" if os.name == "nt" else "venv/bin/pip"

# install dependencies
subprocess.run([pip, "install", "-r", "requirements.txt"], check=True)

# create .env if missing
if not os.path.exists(".env"):
    key = input("\nEnter your NewsAPI key: ").strip()
    with open(".env", "w") as f:
        f.write(f"NEWSAPI_KEY={key}\n")

print("\nSetup complete. Run launch.py to start the dashboard.")
