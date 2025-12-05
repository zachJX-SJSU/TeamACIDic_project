// frontend/src/api/auth.ts
import { api } from "./client";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// This matches FastAPI's OAuth2PasswordRequestForm: form-encoded body
export async function login(username: string, password: string): Promise<TokenResponse> {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const res = await api.post<TokenResponse>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  return res.data;
}

export async function changePassword(data: ChangePasswordRequest): Promise<{ message: string }> {
  const res = await api.post<{ message: string }>("/auth/change-password", data);
  return res.data;
}
