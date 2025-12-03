import axios from "axios";

// Point this to your FastAPI backend.
// In dev on the same EC2 box, usually: http://localhost:8000
// If serving from another host/port, adjust accordingly.
export const api = axios.create({
  baseURL: "http://localhost:8000"
});
