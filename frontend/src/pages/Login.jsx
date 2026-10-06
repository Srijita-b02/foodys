function Login({ role, onBack, onRegister }) {
  function handleSubmit(event) {
    event.preventDefault()
  }

  return (
    <main className="page login-page">
      <button className="back-button" type="button" onClick={onBack}>
        ← Back to roles
      </button>

      <section className="login-card">
        <div className="role-label">{role}</div>
        <h1>Welcome back.</h1>
        <p className="login-copy">Sign in to continue helping your community.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="login">Email or phone number</label>
          <input
            id="login"
            name="login"
            type="text"
            placeholder="Email or phone number"
            autoComplete="username"
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
            Sign in
          </button>
        </form>

        <p className="register-note">
          New here?{' '}
          <button type="button" onClick={onRegister}>
            Create an account
          </button>
        </p>
      </section>
    </main>
  )
}

export default Login
