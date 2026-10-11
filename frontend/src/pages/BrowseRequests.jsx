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
  const [allocations, setAllocations] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [submittingId, setSubmittingId] = useState(null)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    let ignore = false
    const requestPromise = apiRequest('/requests', { token })
    requestPromise
      .then((requestData) => {
        if (!ignore) {
          setRequests(requestData)
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
  }, [canRespond, token])

  async function acceptRequest(event, foodRequest) {
    event.preventDefault()
    setMessage('')
    setIsError(false)

    const requestRemaining =
      foodRequest.remaining_quantity ?? foodRequest.quantity
    const allocatedQuantity = Number(
      allocations[foodRequest.id] ?? requestRemaining,
    )

    if (allocatedQuantity <= 0 || allocatedQuantity > requestRemaining) {
      setIsError(true)
      setMessage(`Enter a quantity between 1 and ${requestRemaining}.`)
      return
    }

    setSubmittingId(foodRequest.id)

    try {
      await apiRequest('/matches/accept-request', {
        method: 'POST',
        token,
        body: {
          request_id: foodRequest.id,
          allocated_quantity: allocatedQuantity,
        },
      })

      const requestData = await apiRequest('/requests', { token })
      setRequests(requestData)
      setAllocations((current) => {
        const updated = { ...current }
        delete updated[foodRequest.id]
        return updated
      })
      setMessage(
        `${allocatedQuantity} ${foodRequest.unit} matched successfully.`,
      )
    } catch (error) {
      setIsError(true)
      setMessage(error.message)
    } finally {
      setSubmittingId(null)
    }
  }

  return (
    <>
      <PageHeader
        title="Open food requests"
        description={
          canRespond
            ? 'Accept a request and enter the quantity you can provide.'
            : 'Open requests from NGO members, shown to help avoid duplicates.'
        }
      />

      {message && (
        <p
          className={`form-message ${isError ? 'form-error' : 'form-success'} page-message`}
          role={isError ? 'alert' : 'status'}
        >
          {message}
        </p>
      )}

      <section className="content-card">
        {isLoading && <p className="empty-state">Loading requests...</p>}

        {!isLoading && requests.length === 0 && (
          <p className="empty-state">No open food requests were found.</p>
        )}

        {requests.map((foodRequest) => {
          const requestRemaining =
            foodRequest.remaining_quantity ?? foodRequest.quantity
          return (
            <div className="request-card" key={foodRequest.id}>
              <div>
                <span className="small-label">{foodRequest.category}</span>
                <h3>{foodRequest.food_name}</h3>
                <p>
                  {requestRemaining} of {foodRequest.quantity}{' '}
                  {foodRequest.unit} still needed · {foodRequest.location}
                </p>
                <p>Needed before {formatDate(foodRequest.needed_before)}</p>
                {foodRequest.description && <p>{foodRequest.description}</p>}
              </div>

              {canRespond && (
                <form
                  className="match-form response-form"
                  onSubmit={(event) => acceptRequest(event, foodRequest)}
                >
                  <label htmlFor={`response-quantity-${foodRequest.id}`}>
                    Quantity ({foodRequest.unit})
                  </label>
                  <input
                    id={`response-quantity-${foodRequest.id}`}
                    type="number"
                    min="1"
                    max={requestRemaining}
                    value={allocations[foodRequest.id] ?? requestRemaining}
                    onChange={(event) =>
                      setAllocations((current) => ({
                        ...current,
                        [foodRequest.id]: event.target.value,
                      }))
                    }
                    required
                  />

                  <button
                    className="outline-button"
                    type="submit"
                    disabled={submittingId === foodRequest.id}
                  >
                    {submittingId === foodRequest.id
                      ? 'Matching...'
                      : 'Accept request'}
                  </button>
                </form>
              )}
            </div>
          )
        })}
      </section>
    </>
  )
}

export default BrowseRequests
