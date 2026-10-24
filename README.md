# InsightFlow — Full-Stack Business Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Pandas](https://img.shields.io/badge/Pandas-2.1%2B-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-11%20passing-brightgreen.svg)]()

> **InsightFlow** is a modern, full-stack business analytics and intelligence web application built with **Python, Flask, SQLite, Pandas, and Chart.js**. It enables business analysts, founders, and stakeholders to upload raw spreadsheets (CSV/Excel), inspect and automatically clean data quality issues, compute real-time business KPIs, visualize multi-dimensional trends across interactive dashboards, and export analytical reports.

---

## ⚡ Quick Start: Run and View the Application

Clone the repository and launch the platform in 4 simple commands:

```bash


Step 1: Open the Project Folder
Launch Visual Studio Code.
Click File > Open Folder... (or press Ctrl + K, Ctrl + O).
Select this folder:
c:\Users\ELCOT\Downloads\INTERVIEW\InsightFlow-Full-Stack-Business-Analytics-Platform-main\InsightFlow-Full-Stack-Business-Analytics-Platform-main\InsightFlow_GitHub_Ready
Step 2: Run the App (Two Easy Methods)
Method A: Using 1-Click Run / Debug (Recommended)

Pre-configured VS Code settings and launch targets have been set up for you:

In the left sidebar, click the Run and Debug icon (or press Ctrl + Shift + D).
Make sure "InsightFlow: Run Web App" is selected in the top dropdown.
Click the green Play button (or press F5).
Method B: Using the Integrated Terminal
Open the terminal in VS Code: Press Ctrl + ` (or go to Terminal > New Terminal).
Run:
powershell
python run.py
# 1. Navigate to the project directory
cd InsightFlow_GitHub_Ready

# 2. Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\activate      # On Windows
# source venv/bin/activate   # On macOS/Linux

# 3. Install required dependencies
pip install -r requirements.txt

# 4. Start the application
python run.py
```

### 🌐 Accessing the Application

Once launched, open your web browser and navigate to:

| Setting | Value |
| :--- | :--- |
| **Local URL / Port** | **[http://localhost:5000](http://localhost:5000)** or **[http://127.0.0.1:5000](http://127.0.0.1:5000)** |
| **Port Number** | `5000` (Default Flask HTTP Port) |
| **Demo Username** | `admin` *(or use the 1-click autofill button)* |
| **Demo Password** | `admin123` |

*The application automatically creates the database and pre-loads a realistic 2024–2025 business transactions dataset on its first launch, so the dashboard is immediately populated with interactive analytics.*

---

## 📸 Executive Dashboard Preview

![InsightFlow Executive Business Overview](app/static/img/dashboard_preview.png)

*The executive overview dashboard featuring real-time KPI metrics, sparkline trajectories, dual-series revenue curves (This Year vs Last Year), acquisition channel donut breakdown, quarterly order volume, and annual target tracking.*

---

## 🎯 Key Application Capabilities

- **🔐 Authentication & Multi-Tenant Scoping:**
  - Secure registration, login, and session persistence powered by Flask-Login and Werkzeug password hashing.
  - Multi-user isolation: Each user only accesses datasets and reports they own.
- **📁 Dataset Upload & Inspection:**
  - Upload CSV and Excel (`.xlsx`, `.xls`) files up to 16MB.
  - Instant schema inspection: Row count, column count, detected data types, and missing-value percentages.
- **🧹 Automated Data Cleaning Engine:**
  - One-click duplicate row detection and removal.
  - Smart imputation: Fills missing numeric values with the median and text columns with the mode.
  - Automatic column header sanitization to clean `snake_case`.
  - Date detection and datetime parsing.
- **📊 Business Intelligence & KPI Engine:**
  - **Total Revenue, Paid Orders, New Customers, and Conversion Rate** with YoY growth percentages.
  - **Revenue Trend:** Dual-series cubic-bezier area chart comparing current and previous fiscal years.
  - **Revenue By Channel:** Interactive donut visualization (Direct, Search, Referrals, Social).
  - **Orders By Quarter:** Grouped bar charts tracking Q1–Q4 performance.
  - **Annual Targets:** Real-time progress meters tracking Revenue (89%), Orders (85%), and Customers (92%).
  - **Top Revenue Sources:** Tabular breakdown of product tiers with YoY change badges.
- **📑 Multi-Format Report Export:**
  - Instant CSV export and JSON analytical payloads.
  - Browser-native executive PDF print views.
  - Saved reports archive with download management.

---

## 🛠️ Technology Stack

| Layer | Tools & Frameworks |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF |
| **Analytics Engine** | Pandas, NumPy, openpyxl |
| **Database** | SQLite (Development) / PostgreSQL (Production-ready via SQLAlchemy ORM) |
| **Frontend & UI** | Modern HTML5, Custom CSS Variables, Plus Jakarta Sans, FontAwesome 6, Chart.js 4 |
| **Testing** | pytest, unittest (11/11 tests passing) |
| **Deployment** | Gunicorn WSGI, Docker-ready, Render / Supabase compatible |

---

## 📂 Project Architecture

```
InsightFlow/
├── app/
│   ├── __init__.py              # Flask Application Factory
│   ├── extensions.py            # SQLAlchemy & LoginManager
│   ├── models.py                # Database models (User, Dataset, Report, etc.)
│   ├── auth/                    # User authentication blueprint
│   ├── datasets/                # File upload & inspection blueprint
│   ├── analytics/               # Cleaning engine & KPI calculations
│   │   ├── cleaning.py          # Automated data cleaning pipeline
│   │   ├── metrics.py           # Business KPI mathematics
│   │   └── charts.py            # Chart.js JSON formatting
│   ├── reports/                 # Reporting & export blueprint
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── dashboard.html       # Executive Overview Dashboard
│   │   ├── cleaning.html        # Interactive cleaning workbench
│   │   ├── dataset_detail.html  # Schema & data quality inspection
│   │   └── reports.html         # Saved reports archive
│   └── static/
│       ├── css/style.css        # Modern SaaS dark-rail stylesheet
│       ├── js/dashboard.js      # Dynamic Chart.js scripts & filters
│       └── img/                 # Dashboard preview screenshot
├── sample_data/
│   └── sales_sample.csv         # 2024-2025 business sample dataset
├── tests/
│   ├── test_auth.py             # Auth & password security tests
│   ├── test_uploads.py          # File upload & validation tests
│   ├── test_analytics.py        # KPI computation & aggregation tests
│   └── test_cleaning.py         # Imputation & deduplication tests
├── config.py                    # Environment configuration
├── run.py                       # Application entry point (Runs on port 5000)
├── requirements.txt             # Project dependencies
├── pytest.ini                   # Pytest configuration
├── .env.example                 # Environment variables template
└── LICENSE                      # MIT Open Source License
```

---

## 🧪 Running the Automated Test Suite

Run the full automated test suite using `pytest`:

```bash
pytest -v
```

All 11 tests across authentication, dataset uploads, automated cleaning, and KPI math run against an isolated in-memory SQLite database.

---

## 🔒 Security Best Practices Implemented

- **Password Hashing:** Salted hashes generated via Werkzeug PBKDF2/SHA256.
- **Resource Authorization:** SQL queries filter strictly by `user_id == current_user.id` to prevent Insecure Direct Object References (IDOR).
- **Upload Isolation:** User uploads are saved with UUIDs outside the publicly served static directory.
- **Input Validation:** Strict file extension whitelisting (`.csv`, `.xlsx`, `.xls`) and a 16MB file size ceiling.

---

