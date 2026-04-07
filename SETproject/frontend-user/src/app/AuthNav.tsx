"use client";

import { useAuth } from "./AuthProvider";

export default function AuthNav() {
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <div className="auth-nav">
        <a href="/auth/login" className="auth-link">Login</a>
        <a href="/auth/register" className="auth-link auth-register">Register</a>
      </div>
    );
  }

  return (
    <div className="auth-nav">
      <span className="auth-user">👤 {user.username}</span>
      <button onClick={logout} className="auth-logout">Logout</button>
    </div>
  );
}
