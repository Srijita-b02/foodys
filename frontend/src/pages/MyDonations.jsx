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

function MyDonations({ token, onNavigate, onEdit }) {
  const [donations, setDonations] = useState([])
  const [allocations, setAllocations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [cancellingId, setCancellingId] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    Promise.all([
      apiRequest('/donations/my', { token }),
      apiRequest('/donations/my/allocations', { token }),
    ])
      .then(([donationData, allocationData]) => {
        if (!ignore) {
          setDonations(donationData)
          setAllocations(allocationData)
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

  async function cancelDonation(donation) {
    const confirmed = window.confirm(
      `Cancel the donation "${donation.food_name}"?`,
    )

    if (!confirmed) {
      return
    }

    setMessage('')
    setCancellingId(donation.id)

    try {
      const cancelled = await apiRequest(`/donations/${donation.id}`, {
        method: 'DELETE',
        token,
      })

      setDonations((current) =>
        current.map((item) => (item.id === cancelled.id ? cancelled : item)),
      )
    } catch (error) {
      setMessage(error.message)
    } finally {
      setCancellingId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="My donations"
        description="Manage your current and previous food donations."
        action={() => onNavigate('donate')}
        actionLabel="New donation"
      />

      {message && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading donations...</p>}

        {!isLoading && donations.length === 0 && (
          <p className="empty-state">
            You have not created any donations yet.
          </p>
        )}

        {donations.map((donation) => {
          const donationAllocations = allocations.filter(
            (allocation) => allocation.donation_id === donation.id,
          )

          return (
            <div className="list-row" key={donation.id}>
              <div>
                <strong>{donation.food_name}</strong>
                <p>
                  {donation.remaining_quantity ?? donation.quantity} of{' '}
                  {donation.quantity} {donation.unit} remaining · Expires{' '}
                  {formatDate(donation.expiry_time)}
                </p>

                {donationAllocations.length > 0 && (
                  <div className="allocation-list">
                    {donationAllocations.map((allocation) => (
                      <div
                        className="allocation-row"
                        key={allocation.match_id}
                      >
                        <div>
                          <span className="allocation-quantity">
                            {allocation.allocated_quantity} {donation.unit}{' '}
                            allocated
                          </span>
                          {allocation.delivery_time && (
                            <span className="allocation-time">
                              Delivered {formatDate(allocation.delivery_time)}
                            </span>
                          )}
                        </div>
                        <StatusBadge status={allocation.delivery_status} />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="row-actions">
                <StatusBadge status={donation.status} />

                {donation.status === 'available' && (
                  <>
                    <button
                      className="secondary-button compact-button"
                      type="button"
                      disabled={cancellingId === donation.id}
                      onClick={() => onEdit(donation.id)}
                    >
                      Edit
                    </button>

                    <button
                      className="danger-button"
                      type="button"
                      disabled={cancellingId === donation.id}
                      onClick={() => cancelDonation(donation)}
                    >
                      {cancellingId === donation.id
                        ? 'Cancelling...'
                        : 'Cancel'}
                    </button>
                  </>
                )}
              </div>
            </div>
          )
        })}
      </section>
    </>
  )
}

export default MyDonations
