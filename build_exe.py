import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
BACKEND_DIR = os.path.join(ROOT_DIR, 'backend')
DIST_OUTPUT_DIR = os.path.join(ROOT_DIR, 'dist')

def run_step(cmd, cwd, step_name):
    print(f"\n==========================================")
    print(f"[STEP] {step_name}")
    print(f"Command: {cmd}")
    print(f"Cwd: {cwd}")
    print(f"==========================================")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"[ERROR] Step '{step_name}' failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    print("==================================================")
    print("  Building Standalone Billing Application (.exe)  ")
    print("==================================================")

    # 1. Build Frontend
    run_step("node node_modules/vite/bin/vite.js build", FRONTEND_DIR, "Building React Frontend (Vite)")

    # Verify static_dist exists
    static_dist = os.path.join(BACKEND_DIR, 'static_dist')
    index_html = os.path.join(static_dist, 'index.html')
    if not os.path.exists(index_html):
        print(f"[ERROR] Expected {index_html} to exist after build!")
        sys.exit(1)
    print("[SUCCESS] React frontend built successfully into backend/static_dist")

    # 2. Package with PyInstaller
    # --onefile creates a single portable .exe
    # --add-data bundles the static frontend assets inside the .exe
    pyinstaller_cmd = (
        f'python -m PyInstaller '
        f'--onefile '
        f'--name BillingApp '
        f'--add-data "static_dist;static_dist" '
        f'--hidden-import reportlab '
        f'--hidden-import waitress '
        f'--hidden-import flask_sqlalchemy '
        f'--hidden-import werkzeug '
        f'--collect-all reportlab '
        f'--collect-all waitress '
        f'launcher.py'
    )
    run_step(pyinstaller_cmd, BACKEND_DIR, "Packaging Backend & UI with PyInstaller")

    # 3. Organize output
    backend_dist_exe = os.path.join(BACKEND_DIR, 'dist', 'BillingApp.exe')
    os.makedirs(DIST_OUTPUT_DIR, exist_ok=True)
    target_exe = os.path.join(DIST_OUTPUT_DIR, 'BillingApp.exe')

    if os.path.exists(backend_dist_exe):
        shutil.copy2(backend_dist_exe, target_exe)
        print(f"\n[BUILD COMPLETE!]")
        print(f"Standalone executable created at:")
        print(f"  --> {target_exe}")
        print("\nYou can now double-click BillingApp.exe to run the application.")
    else:
        print(f"[ERROR] Could not find built executable at {backend_dist_exe}")
        sys.exit(1)

if __name__ == '__main__':
    main()
