// frontend/src/context/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { login as loginApi, TokenResponse } from "../api/auth";

type JwtPayload = {
  emp_no: number;
  is_manager: boolean;
  is_hr_admin: boolean;
  exp: number; // unix timestamp
};

export type AuthUser = {
  empNo: number;
  isManager: boolean;
  isHrAdmin: boolean;
};

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function parseJwt(token: string): JwtPayload {
  const [, payload] = token.split(".");
  const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
  const json = decodeURIComponent(
    atob(base64)
      .split("")
      .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
      .join("")
  );
  return JSON.parse(json);
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);

  // Load from localStorage on first render
  useEffect(() => {
    const stored = localStorage.getItem("access_token");
    if (stored) {
      try {
        const payload = parseJwt(stored);
        const now = Math.floor(Date.now() / 1000);
        if (payload.exp > now) {
          setToken(stored);
          setUser({
            empNo: payload.emp_no,
            isManager: payload.is_manager,
            isHrAdmin: payload.is_hr_admin,
          });
        } else {
          localStorage.removeItem("access_token");
        }
      } catch {
        localStorage.removeItem("access_token");
      }
    }
  }, []);

  const handleLogin = async (username: string, password: string) => {
    const res: TokenResponse = await loginApi(username, password);
    const payload = parseJwt(res.access_token);

    localStorage.setItem("access_token", res.access_token);
    setToken(res.access_token);
    setUser({
      empNo: payload.emp_no,
      isManager: payload.is_manager,
      isHrAdmin: payload.is_hr_admin,
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login: handleLogin,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
