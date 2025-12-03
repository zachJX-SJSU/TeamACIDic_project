// frontend/src/api/client.ts
import axios from "axios";

export const api = axios.create({
  baseURL: "http://54.219.163.78/:8000",
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
