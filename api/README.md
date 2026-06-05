# FinFresh Backend API

This is the backend API service for **FinFresh**, a personal finance tracker application. The service is built with Python using **FastAPI** and **MongoDB** (via the asynchronous Motor client).

---

## 🛠️ Design Decisions & Architecture

### 1. Technology Stack: Python & FastAPI vs. Node.js/Express
We chose **Python** and **FastAPI** over Node.js for several architectural reasons:
* **Python for Financial Computations**: Python's native handling of numeric types, robust math libraries, and standard ecosystem make it highly suited for parsing financial ratios, health scores, and metrics.
* **FastAPI Performance**: FastAPI is one of the fastest Python frameworks available, rivaling Node.js (Express) performance thanks to its underlying `uvicorn` web server and asynchronous execution (`async`/`await`).
* **Self-Documenting API**: FastAPI uses Pydantic schemas to automatically compile interactive OpenAPI documentation (`/docs` and `/redoc`). This speeds up development and client integration.
* **Strong Type Checking and Validation**: Pydantic schemas enforce robust runtime data type validation and error handling, guaranteeing that malformed data is rejected before it touches the business logic or database.

### 2. Project Directory Structure & Separation of Concerns
The codebase is organized following clean architectural principles:
```text
api/
├── app/
│   ├── core/           # Global configuration settings, security parameters, and exception definitions
│   ├── middleware/     # Auth checks, global handler exception catchers, CORS settings
│   ├── models/         # MongoDB collection models mapping document structures
│   ├── routes/         # FastAPI endpoints divided by resource domains (Auth, Transactions, Health, etc.)
│   ├── schemas/        # Pydantic data serialization contracts for inputs/outputs
│   ├── services/       # Core business logic layer (Finance metrics, Authentication flows, Transactions)
│   └── tests/          # Integration & unit test suites
├── env/                # Python Virtual Environment
├── requirements.txt    # Package dependencies list
├── seed_db.py          # Database seeding script
└── uvicorn.exe / main  # Application entry point
```
* **Separation of Concerns**: By dividing the application into Router, Service, Schema, and Model layers, we keep the controllers (Routers) slim. All heavy operations (calculations, queries) are abstracted inside the `services` layer, which makes the code easy to test, maintain, and extend.

### 3. Authentication Implementation
* **Password Security**: Passwords are hashed using the **Bcrypt** algorithm (with a work factor of 12) via `passlib`. Constant-time comparison is used to verify passwords, resisting timing attacks.
* **JSON Web Tokens (JWT)**: Authentication is completely stateless using JWT.
  * **JWT Secret Storage**: Configured via the `JWT_SECRET` key loaded from the `.env` file (managed securely through Pydantic Settings).
  * **Token Expiry**: Set to **60 minutes** by default (`ACCESS_TOKEN_EXPIRE_MINUTES`).
  * **Refresh Tokens**: For this version, only access tokens are implemented to keep the token lifecycle stateless. The frontend intercepts `401 Unauthorized` responses and automatically logs out the user, securing expired sessions immediately.

### 4. Financial Health Score Computation
* **Computation Strategy**: The score is computed **on-demand (dynamically)** via the `GET /api/v1/financial-health` endpoint.
* **Why On-Demand?** 
  * Financial metrics change frequently as transactions are added, edited, or deleted. Computing the score on-demand guarantees that users see the most up-to-date representation of their financial status.
  * The aggregation logic uses fast MongoDB queries. Since we defined optimized indexes on `user_id`, `date`, and `created_at`, these queries remain highly efficient even as transaction history grows.
  * Storing/caching the score in the database would introduce complex cache-invalidation rules (e.g. re-running computations on every transaction update), increasing the risk of stale states.

---

## 🔮 What We Would Do Differently With More Time

1. **Caching Layer (Redis)**:
   * Although on-demand aggregation is fast, introducing a caching layer for `/summary` and `/financial-health` would reduce database load. We would configure cache invalidation based on database mutation events (e.g. creating/deleting a transaction would evict that user's cached summary).
2. **Refresh Token Rotation (RTR)**:
   * To enhance security, we would implement a database-backed refresh token rotation mechanism. This would allow users to stay logged in securely without exposing long-lived access tokens.
3. **Database Migrations (Alembic/Beanie/Motor-Migrations)**:
   * Rather than relying on startup index creation hooks, we would implement formal database schema/index migration tooling to track MongoDB index evolution across environments.
4. **Mocked Testing / Expanded Coverage**:
   * We would introduce unit testing with mock databases (e.g. `mongomock` or a local TestContainers setup) to completely decouple integration testing from physical network connections, making the test suite faster and isolated.

---

## ⚙️ Running Locally

1. **Set Up Environment Variables**:
   In the `api` folder, copy `.env.example` to `.env` and fill in the secrets:
   ```env
   MONGO_URI=your_mongodb_connection_string
   DATABASE_NAME=finance_tracker
   JWT_SECRET=your_jwt_signing_secret
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

2. **Activate Virtual Environment & Run**:
   ```powershell
   # Activate virtualenv (Windows)
   .\env\Scripts\Activate.ps1

   # Run FastAPI server
   python -m uvicorn app.main:app --reload
   ```

3. **Running the Test Suite**:
   ```powershell
   pytest
   ```
