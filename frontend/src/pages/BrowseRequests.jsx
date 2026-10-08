import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader'
import { apiRequest } from '../api'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function sameUnit(first, second) {
  return first.trim().toLocaleLowerCase() === second.trim().toLocaleLowerCase()
}

function BrowseRequests({ token, canRespond }) {
  const [requests, setRequests] = useState([])
  const [donations, setDonations] = useState([])
  const [selectedDonations, setSelectedDonations] = useState({})
  const [allocations, setAllocations] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [submittingId, setSubmittingId] = useState(null)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)

  useEffect(() => {
    let ignore = false
    const requestPromise = apiRequest('/requests', { token })
    const donationPromise = canRespond
      ? apiRequest('/donations/my', { token })
      : Promise.resolve([])

    Promise.all([requestPromise, donationPromise])
      .then(([requestData, donationData]) => {
        if (!ignore) {
          setRequests(requestData)
          setDonations(
            donationData.filter(
              (item) =>
                item.status === 'available' &&
                (item.remaining_quantity ?? item.quantity) > 0,
            ),
          )
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

  async function respondToRequest(event, foodRequest, eligibleDonations) {
    event.preventDefault()
    setMessage('')
    setIsError(false)

    const selectedId = Number(
      selectedDonations[foodRequest.id] ?? eligibleDonations[0]?.id,
    )
    const donation = eligibleDonations.find((item) => item.id === selectedId)

    if (!donation) {
      setIsError(true)
      setMessage(`No available donation uses the unit "${foodRequest.unit}".`)
      return
    }

    const requestRemaining =
      foodRequest.remaining_quantity ?? foodRequest.quantity
    const donationRemaining = donation.remaining_quantity ?? donation.quantity
    const maximum = Math.min(requestRemaining, donationRemaining)
    const allocatedQuantity = Number(
      allocations[foodRequest.id] ?? maximum,
    )

    if (allocatedQuantity <= 0 || allocatedQuantity > maximum) {
      setIsError(true)
      setMessage(`Enter a quantity between 1 and ${maximum}.`)
      return
    }

    setSubmittingId(foodRequest.id)

    try {
      await apiRequest('/matches/respond', {
        method: 'POST',
        token,
        body: {
          donation_id: donation.id,
          request_id: foodRequest.id,
          allocated_quantity: allocatedQuantity,
        },
      })

      const [requestData, donationData] = await Promise.all([
        apiRequest('/requests', { token }),
        apiRequest('/donations/my', { token }),
      ])
      setRequests(requestData)
      setDonations(
        donationData.filter(
          (item) =>
            item.status === 'available' &&
            (item.remaining_quantity ?? item.quantity) > 0,
        ),
      )
      setSelectedDonations((current) => {
        const updated = { ...current }
        delete updated[foodRequest.id]
        return updated
      })
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
            ? 'Select one of your compatible donations to answer a request.'
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
          const eligibleDonations = donations.filter((donation) =>
            sameUnit(donation.unit, foodRequest.unit),
          )
          const selectedId = Number(
            selectedDonations[foodRequest.id] ?? eligibleDonations[0]?.id,
          )
          const selectedDonation = eligibleDonations.find(
            (donation) => donation.id === selectedId,
          )
          const donationRemaining = selectedDonation
            ? selectedDonation.remaining_quantity ?? selectedDonation.quantity
            : 0
          const maximum = Math.min(requestRemaining, donationRemaining)

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

              {canRespond && eligibleDonations.length > 0 && (
                <form
                  className="match-form response-form"
                  onSubmit={(event) =>
                    respondToRequest(event, foodRequest, eligibleDonations)
                  }
                >
                  <label htmlFor={`response-donation-${foodRequest.id}`}>
                    Your donation
                  </label>
                  <select
                    id={`response-donation-${foodRequest.id}`}
                    value={selectedId}
                    onChange={(event) => {
                      const donationId = Number(event.target.value)
                      const nextDonation = eligibleDonations.find(
                        (item) => item.id === donationId,
                      )
                      const nextMaximum = Math.min(
                        requestRemaining,
                        nextDonation?.remaining_quantity ??
                          nextDonation?.quantity ??
                          0,
                      )
                      setSelectedDonations((current) => ({
                        ...current,
                        [foodRequest.id]: donationId,
                      }))
                      setAllocations((current) => ({
                        ...current,
                        [foodRequest.id]: nextMaximum,
                      }))
                    }}
                  >
                    {eligibleDonations.map((donation) => (
                      <option key={donation.id} value={donation.id}>
                        {donation.food_name} —{' '}
                        {donation.remaining_quantity ?? donation.quantity}{' '}
                        {donation.unit}
                      </option>
                    ))}
                  </select>

                  <label htmlFor={`response-quantity-${foodRequest.id}`}>
                    Quantity ({foodRequest.unit})
                  </label>
                  <input
                    id={`response-quantity-${foodRequest.id}`}
                    type="number"
                    min="1"
                    max={maximum}
                    value={allocations[foodRequest.id] ?? maximum}
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
                      : 'Respond'}
                  </button>
                </form>
              )}

              {canRespond && eligibleDonations.length === 0 && (
                <p className="match-note">
                  No available donation uses the unit “{foodRequest.unit}”.
                </p>
              )}
            </div>
          )
        })}
      </section>
    </>
  )
}

export default BrowseRequests
