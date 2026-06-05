# FinFresh Frontend Dashboard

FinFresh is a premium, high-fidelity personal finance tracker dashboard designed to wow users at first glance. It is built on React, Vite, and Tailwind CSS.

---

## 🎨 Frontend Architecture Decisions

To satisfy the requirements of correct functionality, clean structure, reliable error handling, and premium aesthetics, we designed a highly resilient frontend architecture. Here is how we address key development principles:

### 1. Robust State Handling: Loading, Error, and Empty States
Async network calls can fail, delay, or return no data. Rather than having pages render broken/empty tables, we designed three reusable boundary components inside `src/components/`:
* **`LoadingState.jsx`**: Renders a sleek, custom animated spinner with configurable loading helper text, preventing visual layout shifts (jank) while data is being fetched.
* **`ErrorState.jsx`**: Displays a premium warning illustration, an error message, and a **"Try Again" button** which triggers a retry fetch callback.
* **`EmptyState.jsx`**: Displays when query lists are empty (e.g. no transactions matching selected filters). It prompts the user to add transactions, preventing empty white-screen states.

All data-dependent screens (`Dashboard.jsx` and `Transactions.jsx`) orchestrate these states dynamically:
```jsx
if (loading && data.length === 0) return <LoadingState text="Fetching records..." />;
if (error) return <ErrorState message={error} onRetry={fetchData} />;
if (data.length === 0) return <EmptyState message="No transactions found." />;
```

### 2. Defensive Programming: Preventing UI Crashes with Resilient Number Parsing
A common cause of UI failure is type mismatches (e.g. attempting `.toFixed()` or calculations on `null`, `undefined`, or string-coerced numbers from database fields).
* **`src/utils/parseNumber.js`**: We implemented a safe parsing utility that intercepts all numeric fields.
  ```javascript
  export const parseNumber = (value) => {
    if (value === null || value === undefined) return 0;
    const num = Number(value);
    return isNaN(num) ? 0 : num;
  };
  ```
* Every metric card, chart, list, and financial health score indicator routes its raw values through `parseNumber`. This guarantees the UI never throws React render exceptions or displays `NaN`/`Infinity` regardless of raw database format.

### 3. Clean Component Boundaries (Single Responsibility Principle)
Components are atomic, modular, and strictly segregated:
* **Page Layouts (`src/pages/`)**: Responsible for orchestrating page logic, calling API endpoints, keeping local state (loading, filter configs, errors), and passing clean data downwards.
* **Atomic UI Components (`src/components/`)**:
  * **`SummaryCard.jsx`**: Exclusively formats and presents general finance cards (Income, Expenses, Savings) with micro-interactive animations.
  * **`HealthScoreCard.jsx`**: Isolates the canvas/SVG calculations for rendering the health gauge, presenting dynamic advice texts based on rating categories.
  * **`CategoryBreakdown.jsx`**: Groups, formats, and displays the distribution of category spend.
  * **`TransactionTable.jsx`**: Focuses solely on mapping the transactions list into tables, formatting dates, types, and badge colors cleanly.

### 4. Centralized API Layer (`src/services/api.js`)
To prevent scattered API calls and ensure maintainability, all HTTP interactions are consolidated:
* **Single Axios Instance**: Outlines the standard `baseURL` configured via environment variables.
* **Request Interceptor**: Automatically looks up JWT credentials from `localStorage` and appends `Authorization: Bearer <token>` to headers, saving developers from manually copying token logic across fetch requests.
* **Response Interceptor (Self-Healing Session State)**: Detects any `401 Unauthorized` responses (expired/invalid tokens). It immediately drops expired auth files in `localStorage` and redirects the user to the login route. This prevents broken states or API query failures.

### 5. Code Readability & Consistent Naming
We enforced strict styling and naming guidelines to ensure a readable, scalable codebase:
* **PascalCase** for React components (e.g., `TransactionTable`, `HealthScoreCard`).
* **camelCase** for variables, functions, utility files, and hooks (e.g., `parseNumber`, `fetchTransactions`).
* **Upper_Snake_Case** for configuration constants (e.g., `VITE_API_URL`).
* Clear variable and prop names that explain what they contain rather than implementation details.

---

## ⚙️ Running Locally

1. **Set Up Environments**:
   In the `frontend` folder, duplicate `.env.example` as `.env` and enter the API URL:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

2. **Install & Run**:
   ```bash
   # Install dependencies
   npm install

   # Run hot-reloading development server
   npm run dev
   ```
   Open `http://localhost:5174` in your browser.
