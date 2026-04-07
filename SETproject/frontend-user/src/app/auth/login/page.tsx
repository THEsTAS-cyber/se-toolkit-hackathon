"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../AuthProvider";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(username, password);
      router.push("/games");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Login</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="auth-error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>
        <p className="auth-switch">
          No account? <a href="/auth/register">Register</a>
        </p>
      </div>
      <style jsx>{`
        .auth-page {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 80vh;
        }
        .auth-card {
          background: #fff;
          padding: 2rem;
          border-radius: 16px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.1);
          width: 100%;
          max-width: 400px;
        }
        h1 {
          text-align: center;
          margin-bottom: 1.5rem;
          color: #1a1a2e;
        }
        form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        input {
          padding: 0.75rem 1rem;
          border: 2px solid #e0e0e0;
          border-radius: 10px;
          font-size: 1rem;
        }
        input:focus {
          outline: none;
          border-color: #6c5ce7;
        }
        button {
          padding: 0.75rem;
          background: #6c5ce7;
          color: #fff;
          border: none;
          border-radius: 10px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: background 0.2s;
        }
        button:hover:not(:disabled) {
          background: #5a4bd1;
        }
        button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .auth-error {
          color: #e53e3e;
          font-size: 0.85rem;
          text-align: center;
        }
        .auth-switch {
          text-align: center;
          margin-top: 1rem;
          color: #666;
        }
        .auth-switch a {
          color: #6c5ce7;
          text-decoration: none;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}
