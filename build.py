#!/usr/bin/env python3
import subprocess
import sys

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    print(result.stdout)

run_command("pip install -r requirements.txt")
run_command("python manage.py collectstatic --no-input")
run_command("python manage.py migrate")
