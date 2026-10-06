function Register({ role, onBack }) {
  function handleSubmit(event) {
    event.preventDefault()
  }

  return (
    <main className="page login-page">
      <button className="back-button" type="button" onClick={onBack}>
        ← Back to login
      </button>

      <section className="login-card register-card">
        <div className="role-label">{role}</div>
        <h1>Create account.</h1>
        <p className="login-copy">Enter your basic details to get started.</p>

        <form onSubmit={handleSubmit}>
          <label htmlFor="name">Name</label>
          <input
            id="name"
            name="name"
            type="text"
            placeholder="Your name"
            autoComplete="name"
            required
          />

          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            name="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />

          <label htmlFor="phone">Phone number</label>
          <input
            id="phone"
            name="phone"
            type="tel"
            placeholder="Your phone number"
            autoComplete="tel"
            required
          />

          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            name="password"
            type="password"
            placeholder="Create a password"
            autoComplete="new-password"
            required
          />

          <button className="primary-button" type="submit">
            Create account
          </button>
        </form>
      </section>
    </main>
  )
}

export default Register
