import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../api'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function NgoDashboard({ token, onNavigate }) {
  const [requests, setRequests] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest('/requests/my', { token })
      .then((data) => {
        if (!ignore) {
          setRequests(data)
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

  const openCount = requests.filter((item) => item.status === 'open').length
  const matchedCount = requests.filter(
    (item) => item.status === 'matched',
  ).length
  const fulfilledCount = requests.filter(
    (item) => item.status === 'fulfilled',
  ).length

  return (
    <>
      <PageHeader
        title="Overview"
        description="Manage requests, food reservations and deliveries."
        action={() => onNavigate('request')}
        actionLabel="New request"
      />

      <section className="stats-grid">
        <div className="stat-card">
          <span>Open requests</span>
          <strong>{isLoading ? '—' : openCount}</strong>
        </div>

        <div className="stat-card">
          <span>Matched</span>
          <strong>{isLoading ? '—' : matchedCount}</strong>
        </div>

        <div className="stat-card">
          <span>Fulfilled</span>
          <strong>{isLoading ? '—' : fulfilledCount}</strong>
        </div>
      </section>

      {message && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      <section className="content-card">
        <div className="section-heading">
          <div>
            <h2>Recent requests</h2>
            <p>Your latest request activity.</p>
          </div>

          <button
            className="text-button"
            type="button"
            onClick={() => onNavigate('my-requests')}
          >
            View all
          </button>
        </div>

        {isLoading && <p className="empty-state">Loading requests...</p>}

        {!isLoading && requests.length === 0 && (
          <p className="empty-state">No food requests yet.</p>
        )}

        {requests.slice(0, 2).map((foodRequest) => (
          <div className="list-row" key={foodRequest.id}>
            <div>
              <strong>{foodRequest.food_name}</strong>
              <p>
                {foodRequest.quantity} {foodRequest.unit} · Needed before{' '}
                {formatDate(foodRequest.needed_before)}
              </p>
            </div>
            <StatusBadge status={foodRequest.status} />
          </div>
        ))}
      </section>
    </>
  )
}

export default NgoDashboard
