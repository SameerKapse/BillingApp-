import os
import sys
import threading
import time
import webbrowser
from app import app, init_db
from waitress import serve

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:5000"
    print(f"[INFO] Opening browser at {url} ...")
    webbrowser.open(url)

def main():
    print("==================================================")
    print("       Billing & Invoicing Application            ")
    print("==================================================")
    print("[INFO] Initializing SQLite database...")
    init_db()
    
    print("[INFO] Starting application server on http://127.0.0.1:5000")
    print("[INFO] Press Ctrl+C in this console window to exit.")
    
    # Launch browser automatically
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    try:
        serve(app, host='127.0.0.1', port=5000, threads=6)
    except KeyboardInterrupt:
        print("\n[INFO] Application stopped by user.")
        sys.exit(0)

if __name__ == '__main__':
    main()
