import { useState } from 'react'
import RoleSelector from '../components/RoleSelector'

function Register({ role, onRoleChange, onLogin }) {
  const [message, setMessage] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    setMessage(`Mock ${role} registration submitted. No account was created.`)
  }

  function changeRole(nextRole) {
    setMessage('')
    onRoleChange(nextRole)
  }

  return (
    <main className="auth-page register-page">
      <section className="auth-intro">
        <p className="eyebrow">JOIN THE NETWORK</p>
        <h1>Start with the right role.</h1>
        <p>
          Donors share available food. NGO members and volunteers coordinate
          requests and pickup with equal access.
        </p>
        <div className="role-summary">
          <span>Clear roles</span>
          <span>Simple coordination</span>
        </div>
      </section>

      <section className="auth-card register-card" aria-labelledby="register-title">
        <div className="card-heading">
          <p className="section-label">New account</p>
          <h2 id="register-title">Create your profile</h2>
          <p>Select a role and enter the required details.</p>
        </div>

        <RoleSelector value={role} onChange={changeRole} />

        <form onSubmit={handleSubmit}>
          {role === 'Donor' ? (
            <>
              <label htmlFor="donor-name">Name</label>
              <input
                id="donor-name"
                name="name"
                type="text"
                placeholder="Your name"
                autoComplete="name"
                required
              />

              <label htmlFor="donor-type">Donor type</label>
              <select id="donor-type" name="donorType" defaultValue="Individual">
                <option>Individual</option>
                <option>Restaurant</option>
              </select>
            </>
          ) : (
            <>
              <label htmlFor="ngo-name">NGO name</label>
              <input
                id="ngo-name"
                name="ngoName"
                type="text"
                placeholder="Organization name"
                autoComplete="organization"
                required
              />

              <label htmlFor="member-name">Member name</label>
              <input
                id="member-name"
                name="memberName"
                type="text"
                placeholder="Your name"
                autoComplete="name"
                required
              />
            </>
          )}

          <label htmlFor="register-email">Email</label>
          <input
            id="register-email"
            name="email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />

          <label htmlFor="register-password">Password</label>
          <input
            id="register-password"
            name="password"
            type="password"
            placeholder="Create a password"
            autoComplete="new-password"
            minLength="8"
            required
          />

          <label htmlFor="phone">Phone</label>
          <input
            id="phone"
            name="phone"
            type="tel"
            placeholder="Your phone number"
            autoComplete="tel"
            required
          />

          <label htmlFor="location">Location</label>
          <input
            id="location"
            name="location"
            type="text"
            placeholder="Area or locality"
            autoComplete="address-level2"
            required
          />

          <button className="primary-button" type="submit">
            Register as {role}
          </button>
        </form>

        {message && <p className="form-message">{message}</p>}

        <p className="auth-switch">
          Already registered?{' '}
          <button type="button" onClick={onLogin}>
            Sign in
          </button>
        </p>
      </section>
    </main>
  )
}

export default Register
