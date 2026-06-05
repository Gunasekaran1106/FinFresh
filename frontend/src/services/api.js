import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// Request interceptor: attach token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: handle token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/";
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post("/api/v1/auth/register", data),
  login: (data) => api.post("/api/v1/auth/login", data),
  me: () => api.get("/api/v1/auth/me"),
};

// Dashboard endpoints
export const dashboardAPI = {
  getSummary: () => api.get("/api/v1/summary"),
  getFinancialHealth: () => api.get("/api/v1/financial-health"),
};

// Transaction endpoints
export const transactionAPI = {
  create: (data) => api.post("/api/v1/transactions/", data),
  list: (params) => api.get("/api/v1/transactions/", { params }),
  delete: (id) => api.delete(`/api/v1/transactions/${id}`),
};

export default api;
