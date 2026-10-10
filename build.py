import os
import subprocess
import sys

def main():
    print("Building Ninja Collector executable...")

    # Define the PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "NinjaCollector",
        "--add-data", "assets;assets",
        "--add-data", "data;data",
        "main.py"
    ]

    try:
        subprocess.run(cmd, check=True)
        print("\nBuild complete! The standalone executable is located in the 'dist' folder.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
