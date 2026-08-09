"""
PyInstaller Build Script to package the AI/ML Stock Market Screening and Analysis System into a Standalone Windows .exe.
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build():
    print("=" * 60)
    print("Building Standalone Windows Executable using PyInstaller...")
    print("=" * 60)

    python_exe = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = sys.executable

    cmd = [
        str(python_exe), "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=StockMarketScreenerAI",
        "--add-data=app/ml/trained_model.joblib;app/ml",
        "--clean",
        "app/main.py"
    ]

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))

    if result.returncode == 0:
        exe_path = BASE_DIR / "dist" / "StockMarketScreenerAI" / "StockMarketScreenerAI.exe"
        print("\n" + "=" * 60)
        print(f"SUCCESS: Executable successfully built at:\n{exe_path}")
        print("=" * 60)
    else:
        print("\nBUILD FAILED! Check error log above.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
