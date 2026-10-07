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

function MyRequests({ token, onNavigate, onEdit }) {
  const [requests, setRequests] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [cancellingId, setCancellingId] = useState(null)
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

  async function cancelRequest(foodRequest) {
    const confirmed = window.confirm(
      `Cancel the request "${foodRequest.food_name}"?`,
    )

    if (!confirmed) {
      return
    }

    setMessage('')
    setCancellingId(foodRequest.id)

    try {
      const cancelled = await apiRequest(`/requests/${foodRequest.id}`, {
        method: 'DELETE',
        token,
      })

      setRequests((current) =>
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
        title="My requests"
        description="Manage your current and previous food requests."
        action={() => onNavigate('request')}
        actionLabel="New request"
      />

      {message && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading requests...</p>}

        {!isLoading && requests.length === 0 && (
          <p className="empty-state">You have not created any requests yet.</p>
        )}

        {requests.map((foodRequest) => (
          <div className="list-row" key={foodRequest.id}>
            <div>
              <strong>{foodRequest.food_name}</strong>
              <p>
                {foodRequest.quantity} {foodRequest.unit} · Needed before{' '}
                {formatDate(foodRequest.needed_before)}
              </p>
            </div>

            <div className="row-actions">
              <StatusBadge status={foodRequest.status} />

              {foodRequest.status === 'open' && (
                <>
                  <button
                    className="secondary-button compact-button"
                    type="button"
                    disabled={cancellingId === foodRequest.id}
                    onClick={() => onEdit(foodRequest.id)}
                  >
                    Edit
                  </button>

                  <button
                    className="danger-button"
                    type="button"
                    disabled={cancellingId === foodRequest.id}
                    onClick={() => cancelRequest(foodRequest)}
                  >
                    {cancellingId === foodRequest.id
                      ? 'Cancelling...'
                      : 'Cancel'}
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </section>
    </>
  )
}

export default MyRequests
