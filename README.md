# FinFresh — Personal Finance Tracker

**FinFresh** is a premium, high-fidelity personal finance tracker dashboard. It enables users to register, log in, record their income and expense transactions, visualize their spending metrics, and view a dynamically calculated financial health score with actionable recommendations.

The project is split into two main sections:
* 🖥️ [**Frontend (React + Vite + Tailwind CSS)**](file:///e:/Finfresh/FinFresh/frontend/README.md)
* ⚙️ [**Backend API (FastAPI + MongoDB)**](file:///e:/Finfresh/FinFresh/api/README.md)

---

## 🌟 Key Features

* **Premium Glassmorphic Design**: A sleek, dark-themed UI built on a custom aesthetic system using Harmonious HSL colors and dynamic micro-animations.
* **On-Demand Financial Health Analytics**: A score between `0-100` based on key components (Emergency Fund, Savings Rate, Debt Ratio, and Investment Ratio), with specific tips to improve financial habits.
* **Secure stateless Authentication**: State-of-the-art JWT stateless auth, client-side auto-logout on token expiration, and secure Bcrypt password hashing.
* **Category Summaries**: Dynamic transaction filters and a breakdown list detailing exactly where money is allocated.
* **Interactive Transaction Management**: Full list, pagination, and deletion of user records with robust ownership isolation.

---

## 🚀 Quick Start (Development)

### 1. Prerequisite Checks
* Python 3.10+
* Node.js v16+
* MongoDB database (local or MongoDB Atlas connection string)

### 2. Seeding the Database
To populate the database with test data:
1. Navigate to the `api` folder:
   ```bash
   cd api
   ```
2. Copy `.env.example` to `.env` and fill in your `MONGO_URI` and secrets.
3. Run the database seed script:
   ```bash
   # On Windows (PowerShell):
   .\env\Scripts\python seed_db.py
   ```
   This creates two users:
   * **Test User**: `test@example.com` (password: `Str0ng!Pass`)
   * **Moderate User**: `moderate@example.com` (password: `Str0ng!Pass`)

### 3. Running the Backend
1. From the `api` folder, run the web server:
   ```bash
   # On Windows (PowerShell):
   .\env\Scripts\python -m uvicorn app.main:app --reload
   ```
   The backend API will start running on `http://localhost:8000`.

### 4. Running the Frontend
1. Navigate to the `frontend` folder:
   ```bash
   cd ../frontend
   ```
2. Install the node packages:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5174` in your browser to view the application.

---

## 📖 Sub-Project Documentation
For detailed architecture writeups and configuration settings, check the individual project readmes:
* 📝 [**Backend API Documentation**](file:///e:/Finfresh/FinFresh/api/README.md)
* 📝 [**Frontend Dashboard Documentation**](file:///e:/Finfresh/FinFresh/frontend/README.md)