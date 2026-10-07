import { useState } from 'react'
import RoleSelector from '../components/RoleSelector'
import { apiRequest } from '../api'

function Register({ role, onRoleChange, onLogin, onRegistered }) {
  const [message, setMessage] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')
    setIsSubmitting(true)

    const form = new FormData(event.currentTarget)
    const isDonor = role === 'Donor'

    try {
      await apiRequest('/auth/register', {
        method: 'POST',
        body: {
          name: form.get(isDonor ? 'name' : 'memberName').trim(),
          organization_name: isDonor
            ? null
            : form.get('organizationName').trim(),
          email: form.get('email').trim(),
          password: form.get('password'),
          phone: form.get('phone').trim(),
          role: role.toLowerCase(),
          donor_type: isDonor ? form.get('donorType') : null,
          location: form.get('location').trim(),
        },
      })

      onRegistered()
    } catch (error) {
      setMessage(error.message)
    } finally {
      setIsSubmitting(false)
    }
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
          Donors share available food. NGO members coordinate requests,
          pickup and delivery.
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
              <select id="donor-type" name="donorType" defaultValue="individual">
                <option value="individual">Individual</option>
                <option value="restaurant">Restaurant</option>
              </select>
            </>
          ) : (
            <>
              <label htmlFor="ngo-name">NGO name</label>
              <input
                id="ngo-name"
                name="organizationName"
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

          <button
            className="primary-button"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creating account...' : `Register as ${role}`}
          </button>
        </form>

        {message && (
          <p className="form-message form-error" role="alert">
            {message}
          </p>
        )}

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
