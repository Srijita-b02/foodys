import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../api'

const NEXT_STATUS = {
  assigned: {
    status: 'picked_up',
    label: 'Mark as picked up',
  },
  picked_up: {
    status: 'in_transit',
    label: 'Start delivery',
  },
  in_transit: {
    status: 'delivered',
    label: 'Mark as delivered',
  },
}

function formatDate(value) {
  if (!value) {
    return 'Not recorded'
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function Deliveries({ token }) {
  const [deliveries, setDeliveries] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [updatingId, setUpdatingId] = useState(null)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    let ignore = false

    apiRequest('/deliveries/my', { token })
      .then((data) => {
        if (!ignore) {
          setDeliveries(data)
        }
      })
      .catch((error) => {
        if (!ignore) {
          setIsError(true)
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

  async function moveToNextStatus(delivery) {
    const next = NEXT_STATUS[delivery.status]

    if (!next) {
      return
    }

    setMessage('')
    setIsError(false)
    setUpdatingId(delivery.id)

    try {
      const updated = await apiRequest(
        `/deliveries/${delivery.id}/status`,
        {
          method: 'PATCH',
          token,
          body: { status: next.status },
        },
      )

      setDeliveries((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      )
      setMessage(`Delivery updated to ${next.status.replaceAll('_', ' ')}.`)
    } catch (error) {
      setIsError(true)
      setMessage(error.message)
    } finally {
      setUpdatingId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="My deliveries"
        description="Manage only the pickups and deliveries assigned to you."
      />

      {message && (
        <p
          className={`form-message ${isError ? 'form-error' : 'form-success'} page-message`}
          role={isError ? 'alert' : 'status'}
        >
          {message}
        </p>
      )}

      <section className="delivery-list">
        {isLoading && (
          <div className="content-card">
            <p className="empty-state">Loading deliveries...</p>
          </div>
        )}

        {!isLoading && deliveries.length === 0 && (
          <div className="content-card">
            <p className="empty-state">No deliveries are assigned to you.</p>
          </div>
        )}

        {deliveries.map((delivery) => {
          const next = NEXT_STATUS[delivery.status]

          return (
            <article className="delivery-card" key={delivery.id}>
              <div className="delivery-card-header">
                <div>
                  <span className="small-label">
                    {delivery.request_id
                      ? 'DONOR RESPONSE'
                      : 'DIRECT RESERVATION'}
                  </span>
                  <h2>{delivery.food_name}</h2>
                  <p>
                    {delivery.allocated_quantity} {delivery.unit} · Donor:{' '}
                    {delivery.donor_name}
                  </p>
                </div>

                <StatusBadge status={delivery.status} />
              </div>

              <div className="delivery-route">
                <div>
                  <span>Pickup</span>
                  <strong>{delivery.pickup_address}</strong>
                </div>
                <div aria-hidden="true">→</div>
                <div>
                  <span>Destination</span>
                  <strong>{delivery.destination_location}</strong>
                </div>
              </div>

              <div className="delivery-meta">
                <span>Assigned: {formatDate(delivery.assigned_at)}</span>
                <span>Picked up: {formatDate(delivery.pickup_time)}</span>
                <span>Delivered: {formatDate(delivery.delivery_time)}</span>
              </div>

              {next && (
                <button
                  className="orange-button delivery-action"
                  type="button"
                  disabled={updatingId === delivery.id}
                  onClick={() => moveToNextStatus(delivery)}
                >
                  {updatingId === delivery.id ? 'Updating...' : next.label}
                </button>
              )}
            </article>
          )
        })}
      </section>
    </>
  )
}

export default Deliveries
