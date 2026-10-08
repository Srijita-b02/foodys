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

function DonorDashboard({ token, onNavigate }) {
  const [donations, setDonations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest('/donations/my', { token })
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

  const activeStatuses = new Set([
    'available',
    'reserved',
    'matched',
    'assigned',
    'picked_up',
    'in_transit',
  ])
  const activeCount = donations.filter((item) =>
    activeStatuses.has(item.status),
  ).length
  const reservedCount = donations.filter(
    (item) => item.status === 'reserved',
  ).length
  const deliveredCount = donations.filter(
    (item) => item.status === 'delivered',
  ).length

  return (
    <>
      <PageHeader
        title="Overview"
        description="A quick look at your food sharing activity."
        action={() => onNavigate('donate')}
        actionLabel="New donation"
      />

      <section className="stats-grid">
        <div className="stat-card">
          <span>Active donations</span>
          <strong>{isLoading ? '—' : activeCount}</strong>
        </div>

        <div className="stat-card">
          <span>Reserved</span>
          <strong>{isLoading ? '—' : reservedCount}</strong>
        </div>

        <div className="stat-card">
          <span>Delivered</span>
          <strong>{isLoading ? '—' : deliveredCount}</strong>
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
            <h2>Recent donations</h2>
            <p>Your latest food listings.</p>
          </div>

          <button
            className="text-button"
            onClick={() => onNavigate('donations')}
          >
            View all
          </button>
        </div>

        {isLoading && <p className="empty-state">Loading donations...</p>}

        {!isLoading && donations.length === 0 && (
          <p className="empty-state">No donations yet.</p>
        )}

        {donations.slice(0, 2).map((donation) => (
          <div className="list-row" key={donation.id}>
            <div>
              <strong>{donation.food_name}</strong>
              <p>
                {donation.remaining_quantity ?? donation.quantity} of{' '}
                {donation.quantity} {donation.unit} remaining · Expires{' '}
                {formatDate(donation.expiry_time)}
              </p>
            </div>

            <StatusBadge status={donation.status} />
          </div>
        ))}
      </section>
    </>
  )
}

export default DonorDashboard
