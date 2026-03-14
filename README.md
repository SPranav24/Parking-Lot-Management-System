# Parking Lot Management System 🚗🏍️

A comprehensive, web-based Multi-Parking System built with Python and Flask. This system allows administrators to dynamically configure parking floors and slots for different vehicle types (Cars and Bikes), actively manage vehicular entry/exit, calculate dynamic parking fees, and view real-time occupancy dashboards and analytics.

---

## 🌟 Key Features

*   **Dynamic Floor Scaling:** Admins can add and remove multiple parking floors in real-time.
*   **Slot Allocation:** Configurable capacities tailored specifically for Bikes or Cars on each individual floor.
*   **Vehicle Entry/Exit Tracking:** Seamlessly generates digital tickets documenting entry time, exit time, and parking durations.
*   **Dynamic Pricing Engine:** Admins can define custom hourly rates for different vehicle classifications, which automatically calculate at checkout.
*   **Multi-User Administration:** Secure registration and login flows isolated by user accounts; each admin controls their own isolated parking facility setup.
*   **Real-time Analytics Dashboard:** Live heatmaps and capacity status indicators for all active parking slots across the facility.
*   **Persistent Ticket History:** A robust search gateway to query historical parking records by vehicle registration numbers.

---

## 💻 Tech Stack

*   **Backend:** Python 3, Flask
*   **Database:** SQLite (Local Testing), PostgreSQL / MySQL (Production via Flask-SQLAlchemy)
*   **Frontend UI:** HTML5, modern CSS3 styling, Jinja2 templating, Bootstrap via CDN
*   **Authentication:** Flask-Login, Werkzeug Security (PBKDF2 SHA256 Hashing)
*   **Deployment Integration:** Gunicorn

---

## 🚀 Local Installation & Setup

Want to run this system locally on your own machine? Follow these steps:

### 1. Clone the repository
```bash
git clone https://github.com/SPranav24/Parking-Lot-Management-System.git
cd Parking-Lot-Management-System
```

### 2. Create a Virtual Environment (Recommended but optional)
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application!
```bash
python app.py
```
*The server will start up. You can view the app in your browser at `http://127.0.0.1:5000`*

---
🌐 Live Demo

🔗 Try the deployed application:
https://parking-lot-management-system-l3uv.onrender.com/

## ☁️ Deployment Guide (Render)

This application is fully pre-configured for deployment on cloud platforms using Gunicorn and PostgreSQL.

1. Create a free **PostgreSQL Database** on Render.
2. Link this GitHub repository to a new **Web Service** on Render.
3. Use the following configuration:
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app` (or rely on the included `Procfile`)
4. Add an **Environment Variable**:
    *   **Key:** `DATABASE_URL` 
    *   **Value:** `[Your Render Internal Database URL]`
5. **Deploy!**

---

## 📸 Core Modules
1. **User Auth (`/login`, `/signup`)** - Secure encrypted admin access.
2. **Configuration (`/manage_floors`)** - Command center to edit floor capacities and base pricing.
3. **Operations (`/park`, `/exit`)** - Core functions to log incoming and departing vehicles.
4. **Dashboard (`/dashboard`)** - Live capacity monitoring and summary data. 

---
*Built as a scalable infrastructure management platform. Premium Edition v2.0.*
