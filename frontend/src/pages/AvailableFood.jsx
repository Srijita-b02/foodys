import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function AvailableFood({ token }) {
  const [donations, setDonations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest('/donations', { token })
      .then((data) => {
        if (!ignore) {
          setDonations(data)
        }
      })
      .catch((error) => {
        if (!ignore) {
          setMessage(error.message)
        }
      })
      .finally(() => {
        if (!ignore) {
          setIsLoading(false)
        }
      })

    return () => {
      ignore = true
    }
  }, [token])

  return (
    <>
      <PageHeader
        title="Available food"
        description="Surplus food currently available from donors."
      />

      {message && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading available food...</p>}

        {!isLoading && donations.length === 0 && (
          <p className="empty-state">No food is currently available.</p>
        )}

        {donations.map((donation) => (
          <div className="request-card" key={donation.id}>
            <div>
              <span className="small-label">{donation.category}</span>
              <h3>
                {donation.quantity} {donation.unit} of {donation.food_name}
              </h3>
              <p>
                {donation.pickup_address} · Available until{' '}
                {formatDate(donation.expiry_time)}
              </p>
              {donation.description && <p>{donation.description}</p>}
            </div>

            <button
              className="orange-button"
              type="button"
              disabled
              title="Reservation will be connected in the matching step"
            >
              Reserve
            </button>
          </div>
        ))}
      </section>
    </>
  )
}

export default AvailableFood
