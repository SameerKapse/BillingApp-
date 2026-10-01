<<<<<<< HEAD
# Full-Stack Billing & Invoicing System (React + Flask + SQLite + .exe)

A modern, full-stack billing and invoicing desktop web application built with **React** on the frontend, **Flask & SQLite** on the backend, and packaged into a standalone Windows **`.exe`** using **PyInstaller** and **Waitress**.

---

## 🌟 Key Features

- **Authentication & Multi-user Support**:
  - Secure login and registration with hashed passwords (`werkzeug.security`).
  - Pre-seeded default admin account (`admin` / `admin123`).
- **Interactive Billing Dashboard**:
  - Customer contact and billing address management.
  - Dynamic line items (add/remove rows, quantity, unit price).
  - Automatic calculation of subtotal, configurable tax rate (%), tax amount, and grand total.
  - Notes and payment terms field.
- **Persistent Database Storage**:
  - SQLite database (`data/billing.db`) persists all customer details, items, invoice numbers, and financial totals.
  - Invoices history table with real-time search and filter.
- **Professional PDF Invoice Generation**:
  - Generates downloadable PDF invoices using ReportLab.
  - Automatic download immediately upon saving the bill.
  - Ability to re-download past invoices from the history tab anytime.
- **Standalone Windows Executable (`.exe`)**:
  - The React frontend is compiled and embedded directly into the Flask application.
  - A single `.exe` runs both the backend server and UI, and automatically opens your default web browser on launch.

---

## 📁 Project Structure

```text
billing-system/
├── backend/
│   ├── app.py              # Flask REST API & static asset server
│   ├── models.py           # SQLAlchemy User and Bill models
│   ├── pdf_generator.py    # ReportLab PDF invoice generator
│   ├── launcher.py         # Waitress server launcher & auto-browser opener
│   ├── requirements.txt    # Python dependencies
│   └── data/               # Persistent SQLite DB and generated PDFs (auto-created)
│       ├── billing.db
│       └── invoices/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx         # Root component with navigation & auth state
│       ├── api.js          # API client for authentication & billing
│       ├── index.css       # Clean, modern UI styling
│       ├── main.jsx
│       └── components/
│           ├── Login.jsx       # Login & Register modal
│           ├── BillingForm.jsx # Invoice creation form & dynamic rows
│           └── BillsHistory.jsx# Table of past invoices with PDF download
├── build_exe.py            # Automated build script (React build + PyInstaller)
├── build_exe.bat           # 1-click Windows batch script to build .exe
├── run_dev.bat             # 1-click script to run in development mode
└── README.md
```

---

## 🚀 How to Run the Application

### Option 1: Run the Standalone `.exe` (Recommended)

1. **Build the `.exe` (if not already built)**:
   Double-click `build_exe.bat` or run:
   ```cmd
   python build_exe.py
   ```
   This will compile the React frontend into `backend/static_dist` and run PyInstaller to bundle everything into:
   ```
   dist\BillingApp.exe
   ```

2. **Run `BillingApp.exe`**:
   - Double-click `dist\BillingApp.exe`.
   - The application will automatically:
     - Initialize the SQLite database at `data/billing.db`.
     - Start the production Waitress server on `http://127.0.0.1:5000`.
     - Automatically open your default web browser to the login page.
   - To stop the application, simply press `Ctrl+C` in the command window.

---

### Option 2: Run in Development Mode (Live Hot-Reload)

If you want to modify code and see instant updates:

1. **Start Backend**:
   ```cmd
   cd backend
   python -m pip install -r requirements.txt
   python app.py
   ```
   *Backend runs on `http://127.0.0.1:5000`*

2. **Start Frontend (in a new terminal)**:
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```
   *Frontend runs on `http://127.0.0.1:5173` and proxies `/api` calls to Flask.*

Or simply double-click `run_dev.bat`.

---

## 🔐 Default Credentials

| Username | Password   | Role         |
|----------|------------|--------------|
| `admin`  | `admin123` | Administrator|

*You can also click "Register" on the login screen to create your own account.*

---

## 📡 API Endpoints Reference

| Method | Endpoint                    | Description                                  |
|--------|-----------------------------|----------------------------------------------|
| `POST` | `/api/login`                | Authenticate user                            |
| `POST` | `/api/register`             | Register a new account                       |
| `POST` | `/api/logout`               | Terminate current session                    |
| `GET`  | `/api/me`                   | Check session status and current user info   |
| `GET`  | `/api/bills`                | List all saved bills (supports `?search=...`)|
| `POST` | `/api/bills`                | Create & save bill to DB, generate PDF       |
| `GET`  | `/api/bills/<id>`           | Get specific bill details                    |
| `GET`  | `/api/bills/<id>/download`  | Download generated PDF invoice               |

---

## 🛠️ Customization

- **Change Business Name / Header in PDF**:
  Open `backend/pdf_generator.py` and modify `YOUR BUSINESS NAME`, address, and contact details in `header_data`.
- **Change Currency or Default Tax Rate**:
  Open `frontend/src/components/BillingForm.jsx` and adjust the default state `taxRate = 10`.
=======
# BillingApp-
Security testing
>>>>>>> 4b6149436c350b9c485e4302a094fedf7c412ffb
