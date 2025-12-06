// frontend/src/api/client.ts
import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8001",
});

// Attach Authorization: Bearer <token> on every request if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
