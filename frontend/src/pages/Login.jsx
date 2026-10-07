import { useState } from 'react'
import RoleSelector from '../components/RoleSelector'

function Login({ role, onRoleChange, onRegister, onLogin }) {
  const [message, setMessage] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    onLogin()
    // setMessage(`Mock ${role} login submitted. No account was accessed.`)
  }

  return (
    <main className="auth-page">
      <section className="auth-intro">
        <p className="eyebrow">SDG 2 · ZERO HUNGER</p>
        <h1>Food shared with purpose.</h1>
        <p>
          A simple place for donors and NGOs to coordinate surplus food and
          community needs.
        </p>
        <div className="role-summary">
          <span>2 roles</span>
          <span>1 shared mission</span>
        </div>
      </section>

      <section className="auth-card" aria-labelledby="login-title">
        <div className="card-heading">
          <p className="section-label">Account access</p>
          <h2 id="login-title">Welcome back</h2>
          <p>Choose your role and sign in.</p>
        </div>

        <RoleSelector value={role} onChange={onRoleChange} />

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            placeholder="Enter your password"
            autoComplete="current-password"
            required
          />

          <button className="primary-button" type="submit">
            Sign in as {role}
          </button>
        </form>

        {message && <p className="form-message">{message}</p>}

        <p className="auth-switch">
          Need an account?{' '}
          <button type="button" onClick={onRegister}>
            Register
          </button>
        </p>
      </section>
    </main>
  )
}

export default Login
