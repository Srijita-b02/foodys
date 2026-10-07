import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function BrowseRequests({ token, canRespond }) {
  const [requests, setRequests] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [message, setMessage] = useState('')

  useEffect(() => {
    let ignore = false

    apiRequest('/requests', { token })
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

  return (
    <>
      <PageHeader
        title="Open food requests"
        description={
          canRespond
            ? 'Requests that may match your available donations.'
            : 'Open requests from NGO members, shown to help avoid duplicates.'
        }
      />

      {message && (
        <p className="form-message form-error page-message" role="alert">
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading requests...</p>}

        {!isLoading && requests.length === 0 && (
          <p className="empty-state">No open food requests were found.</p>
        )}

        {requests.map((foodRequest) => (
          <div className="request-card" key={foodRequest.id}>
            <div>
              <span className="small-label">{foodRequest.category}</span>
              <h3>
                {foodRequest.quantity} {foodRequest.unit} of{' '}
                {foodRequest.food_name}
              </h3>
              <p>
                {foodRequest.location} · Needed before{' '}
                {formatDate(foodRequest.needed_before)}
              </p>
              {foodRequest.description && <p>{foodRequest.description}</p>}
            </div>

            {canRespond && (
              <button
                className="outline-button"
                type="button"
                disabled
                title="Donor response will be connected in the matching step"
              >
                Respond
              </button>
            )}
          </div>
        ))}
      </section>
    </>
  )
}

export default BrowseRequests
