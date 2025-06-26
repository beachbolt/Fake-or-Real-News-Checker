import subprocess

# Launch backend
subprocess.Popen(["python", "backend.py"])

# Launch clipboard analyzer
subprocess.Popen(["python", "clipboard_analyzer.py"])