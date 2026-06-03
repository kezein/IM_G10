# Profriends Inc. — Housing Loan Management System

A web-based housing loan management system built for **IM Group 10**.  
Manages buyers, loan applications, property listings, payments, and beneficiaries through a single-page application backed by a Flask REST API and MySQL database.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

---

## Prerequisites

Before setting up, make sure these are installed on your machine:

- **Python 3.10+** — [python.org](https://www.python.org/downloads/)
- **MySQL 8.0+** — [mysql.com](https://dev.mysql.com/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)

---

## Setup Guide

### 1. Clone the repository

```bash
git clone https://github.com/kezein/IM_G10.git
cd IM_G10
```

### 2. Set up the MySQL database

Open MySQL and run the schema file to create the database and tables:

```bash
mysql -u root -p < database/profriends_inc.sql
```

### 3. Create the environment file

Inside the `backend/` folder, create a file named `.env`:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=profriends_inc
ADMIN_USER=admin
ADMIN_PASS=admin
```

> Change `DB_PASSWORD` to your actual MySQL root password.

### 4. Create and activate a virtual environment

```bash
cd backend
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the server

```bash
python app.py
```

The server starts at **http://localhost:5000**

### 7. Open the app

Navigate to **http://localhost:5000** in your browser.

---

## Default Login Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin` |
| Buyer | `B-YYYY-###` (Buyer ID) | Last name of buyer |

---

## Project Structure

```
IM_G10/
├── backend/
│   ├── app.py              # Flask entry point
│   ├── config.py           # DB config loader
│   ├── db.py               # MySQL connection helper
│   ├── requirements.txt    # Python dependencies
│   ├── routes/             # API route handlers
│   ├── static/             # Static assets (photos)
│   └── templates/
│       └── index.html      # Single-page application
├── database/
│   ├── profriends_inc.sql          # Schema + seed data
│   └── profriends_inc_queries.sql  # Report queries
└── README.md
```

---

## Team

| Name | Role | Contributions |
|---|---|---|
| **Lawrence** | Flask Backend / Python | Flask REST API, MySQL integration, backend-frontend wiring, UI redesign & green theme |
| **Andrei** | Frontend | SPA architecture, UI components, page layout and design |
| **Izy** | Database & SQL | Database schema design, SQL report queries |
| **Kezia** | Backend Integration | Backend integration, API connection, system wiring |
| **Paul** | Documentation & Integration | System documentation, integration support |

---

## Features

**Admin Portal**
- Manage buyers (add, edit, delete)
- Manage loan applications (approve, reject, track)
- Manage property listings
- View sales and outstanding payment reports

**Buyer Portal**
- View account details
- View reserved property
- Track loan details and remaining balance
- View payment history
- Manage beneficiaries
- Apply for new loan

---

*IM Group 10 — Information Management*
