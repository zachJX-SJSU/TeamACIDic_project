import React, { useState } from "react";

const API_BASE = "http://127.0.0.1:8000"; // backend FastAPI URL
const LOGIN_PATH = "/auth/login";         // confirm with Zach/Swagger
const CHANGE_PW_PATH = "/auth/change-password"; // confirm with Zach/Swagger

function App() {
  const [page, setPage] = useState("login"); // "login" or "changePassword"
  const [username, setUsername] = useState("");
  const [token, setToken] = useState(null); // whatever the backend returns (JWT, etc.)

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>TeamACIDic HR Portal</h1>

      <div style={styles.tabs}>
        <button
          style={page === "login" ? styles.tabActive : styles.tab}
          onClick={() => setPage("login")}
        >
          Log in
        </button>
        <button
          style={page === "changePassword" ? styles.tabActive : styles.tab}
          onClick={() => setPage("changePassword")}
          disabled={!token}
          title={!token ? "Log in first to change password" : ""}
        >
          Change Password
        </button>
      </div>

      <div style={styles.card}>
        {page === "login" ? (
          <LoginForm
            setPage={setPage}
            setUsername={setUsername}
            setToken={setToken}
          />
        ) : (
          <ChangePasswordForm username={username} token={token} />
        )}
      </div>
    </div>
  );
}

function LoginForm({ setPage, setUsername, setToken }) {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    if (!form.username.trim()) {
      return "Username is required";
    }
    if (form.password.length < 6 || form.password.length > 12) {
      return "Password must be 6–12 characters long";
    }
    return "";
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const err = validate();
    if (err) {
      setError(err);
      return;
    }

    try {
      setLoading(true);
      const resp = await fetch(API_BASE + LOGIN_PATH, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        setError(data.detail || "Login failed");
        return;
      }

      const data = await resp.json();
      // Adjust based on what Zach's login endpoint returns:
      setToken(data.token || data.access_token || true);
      setUsername(form.username);

      if (form.password === "abc123") {
        // Default password: force change-password flow
        setPage("changePassword");
      }
    } catch (err) {
      console.error(err);
      setError("Network error – is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} style={styles.form}>
      <h2>Log in</h2>
      <p style={styles.hint}>
        Default admin: <b>admin00 / abc123</b>
      </p>

      <label style={styles.label}>
        Username
        <input
          style={styles.input}
          name="username"
          value={form.username}
          onChange={onChange}
          placeholder="e.g. zx007"
        />
      </label>

      <label style={styles.label}>
        Password
        <input
          style={styles.input}
          type="password"
          name="password"
          value={form.password}
          onChange={onChange}
          placeholder="6–12 characters"
        />
      </label>

      {error && <div style={styles.error}>{error}</div>}

      <button type="submit" style={styles.button} disabled={loading}>
        {loading ? "Logging in..." : "Log in"}
      </button>
    </form>
  );
}

function ChangePasswordForm({ username, token }) {
  const [form, setForm] = useState({
    old_password: "",
    new_password: "",
  });
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    if (!form.old_password) return "Old password is required";
    if (form.new_password.length < 6 || form.new_password.length > 12) {
      return "New password must be 6–12 characters long";
    }
    if (form.new_password === form.old_password) {
      return "New password must be different from old password";
    }
    return "";
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    const err = validate();
    if (err) {
      setError(err);
      return;
    }

    try {
      setLoading(true);
      const resp = await fetch(API_BASE + CHANGE_PW_PATH, {
        method: "POST", // or PUT, match Zach's API
        headers: {
          "Content-Type": "application/json",
          // If Zach uses auth tokens, add them here:
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          username,
          old_password: form.old_password,
          new_password: form.new_password,
        }),
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => ({}));
        setError(data.detail || "Change password failed");
        return;
      }

      setMessage("Password updated successfully!");
      setForm({ old_password: "", new_password: "" });
    } catch (err) {
      console.error(err);
      setError("Network error – is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={onSubmit} style={styles.form}>
      <h2>Change Password</h2>
      <p style={styles.hint}>
        Logged in as: <b>{username || "(unknown user)"}</b>
      </p>

      <label style={styles.label}>
        Old password
        <input
          style={styles.input}
          type="password"
          name="old_password"
          value={form.old_password}
          onChange={onChange}
        />
      </label>

      <label style={styles.label}>
        New password
        <input
          style={styles.input}
          type="password"
          name="new_password"
          value={form.new_password}
          onChange={onChange}
          placeholder="6–12 characters"
        />
      </label>

      {error && <div style={styles.error}>{error}</div>}
      {message && <div style={styles.success}>{message}</div>}

      <button type="submit" style={styles.button} disabled={loading || !username}>
        {loading ? "Updating..." : "Update password"}
      </button>
    </form>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "flex-start",
    background: "#f5f5f5",
    paddingTop: "40px",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
  },
  title: {
    marginBottom: "20px",
  },
  tabs: {
    display: "flex",
    gap: "8px",
    marginBottom: "16px",
  },
  tab: {
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    background: "white",
    cursor: "pointer",
  },
  tabActive: {
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #007bff",
    background: "#e6f0ff",
    cursor: "pointer",
  },
  card: {
    width: "100%",
    maxWidth: "400px",
    padding: "24px",
    borderRadius: "12px",
    background: "white",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "12px",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    fontSize: "14px",
  },
  input: {
    marginTop: "4px",
    padding: "8px 10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  button: {
    marginTop: "8px",
    padding: "10px 16px",
    border: "none",
    borderRadius: "999px",
    background: "#007bff",
    color: "white",
    fontWeight: "600",
    cursor: "pointer",
  },
  error: {
    padding: "8px",
    borderRadius: "6px",
    background: "#ffe6e6",
    color: "#b00020",
    fontSize: "13px",
  },
  success: {
    padding: "8px",
    borderRadius: "6px",
    background: "#e6ffea",
    color: "#006400",
    fontSize: "13px",
  },
  hint: {
    fontSize: "12px",
    color: "#666",
  },
};

export default App;
