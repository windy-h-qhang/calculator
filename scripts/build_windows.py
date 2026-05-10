import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "CalculatorSuite"
ROOT_DIR = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT_DIR / "windows_app"
WORK_DIR = ROOT_DIR / "build" / "pyinstaller"
SPEC_DIR = WORK_DIR / "specs"


def main():
    if sys.platform != "win32":
        raise SystemExit("Windows 软件包需要在 Windows 环境中构建。")

    ensure_pyinstaller()
    clean_previous_build()

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name",
        APP_NAME,
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(WORK_DIR),
        "--specpath",
        str(SPEC_DIR),
        "--add-data",
        data_arg("frontends/django_web/templates", "frontends/django_web/templates"),
        "--collect-submodules",
        "django",
        "--collect-submodules",
        "sympy",
        "--collect-data",
        "django",
        str(ROOT_DIR / "main.py"),
    ]

    subprocess.run(command, cwd=ROOT_DIR, check=True)
    print(f"打包完成: {DIST_DIR / APP_NAME}")


def ensure_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise SystemExit("缺少 PyInstaller，请先运行: python -m pip install pyinstaller") from exc


def clean_previous_build():
    shutil.rmtree(DIST_DIR / APP_NAME, ignore_errors=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    SPEC_DIR.mkdir(parents=True, exist_ok=True)


def data_arg(source, target):
    return f"{ROOT_DIR / source}{os.pathsep}{target}"


if __name__ == "__main__":
    main()
