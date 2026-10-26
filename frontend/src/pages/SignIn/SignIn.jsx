import { useState } from "react";
import { useAuth } from "../../context/Auth";
import { Notice } from "../../components/ui/Shared";
import "./SignIn.css";
export default function SignIn() {
  const { login } = useAuth(),
    [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    try {
      await login(email, password);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="signin">
      <div className="signin-story">
        <span className="eyebrow">RevenueOps Intelligence</span>
        <h1>
          Financial clarity.
          <br />
          Human confidence.
        </h1>
        <p>
          A considered workspace for reconciliation, investigation and
          responsible collections.
        </p>
        <small>
          Deterministic finance · CrewAI investigation · Human approval
        </small>
      </div>
      <section className="signin-form">
        <h2>Welcome back.</h2>
        <p className="muted">Sign in to your finance workspace.</p>
        <form onSubmit={submit}>
          <label>
            Email
            <input
              type="email"
              autoComplete="username"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error && <Notice error>{error}</Notice>}
          <button disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
        </form>
        <p className="signin-foot">
          Synthetic demo credentials are documented in the project README. No
          real customer data is included.
        </p>
      </section>
    </div>
  );
}
